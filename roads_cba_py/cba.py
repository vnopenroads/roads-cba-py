import numpy as np

from .cba_result import CbaResult
from .defaults import (
    dDiscount_Rate,
    dEconomic_Factor,
    dGrowth,
    dTrafficLevels,
    dVehicleFleet,
    iSurfaceDefaults,
    dWidthDefaults,
    dConditionData,
    dRoadWorks,
    dRecurrent,
    dRecMult,
    dWorkEvaluated,
    dm_coeff,
    dVOC,
    dSPEED,
    dRoadDet,
    iri_cc_df,
    get_cc_from_iri,
)
from .section import Section


class CostBenefitAnalysisModel:
    def __init__(self):
        self.dDiscount_Rate = dDiscount_Rate
        self.dEconomic_Factor = dEconomic_Factor
        self.dGrowth = dGrowth
        self.dTrafficLevels = dTrafficLevels
        self.dVehicleFleet = dVehicleFleet
        self.iSurfaceDefaults = iSurfaceDefaults
        self.dWidthDefaults = dWidthDefaults
        self.dConditionData = dConditionData
        self.dRoadWorks = dRoadWorks
        self.dRecurrent = dRecurrent
        self.dRecMult = dRecMult
        self.dWorkEvaluated = dWorkEvaluated
        self.dm_coeff = dm_coeff
        self.dVOC = dVOC
        self.dSPEED = dSPEED
        self.dRoadDet = dRoadDet
        self.iri_cc_df = iri_cc_df

    def compute_cba_for_section(self, section: Section) -> CbaResult:
        """
        Main entry to computer Cost Benefit Analysis for each road section
        """

        # Step 1: Get input attributes from section
        dLength = section.length
        iLanes = section.lanes
        dWidth = section.width
        iRoadClass = section.road_class
        iTerrain = section.terrain
        iTemperature = section.temperature
        iMoisture = section.moisture
        iRoadType = section.road_type
        iSurfaceType = section.surface_type
        iConditionClass = section.condition_class
        dRoughness = self.get_initial_roughness(section)

        dStructuralNo = section.structural_no
        iPavementAge = section.pavement_age
        iDrainageClass = None
        iTrafficLevel = section.traffic_level
        iGrowthScenario = section.traffic_growth

        dAADT = np.zeros((13, 20), dtype=np.float64)
        dAADT[0][0] = section.aadt_motorcyle
        dAADT[1][0] = section.aadt_carsmall
        dAADT[2][0] = section.aadt_carmedium
        dAADT[3][0] = section.aadt_delivery
        dAADT[4][0] = section.aadt_4wheel
        dAADT[5][0] = section.aadt_smalltruck
        dAADT[6][0] = section.aadt_mediumtruck
        dAADT[7][0] = section.aadt_largetruck
        dAADT[8][0] = section.aadt_articulatedtruck
        dAADT[9][0] = section.aadt_smallbus
        dAADT[10][0] = section.aadt_mediumbus
        dAADT[11][0] = section.aadt_largebus
        dAADT[12][0] = section.aadt_total

        iNoAlernatives, dAlternatives = self.compute_alternatives(iSurfaceType, iRoadClass, iConditionClass)

        dCostFactor = self.compute_cost_factor(iSurfaceType, iRoadClass, iConditionClass)

        # Annual traffic
        dAADT = self.compute_annual_traffic(dAADT, iGrowthScenario)
        # ESA Loading
        dESATotal = self.compute_esa_loading(dAADT, iLanes)
        # Truck percent
        dTRucks = self.compute_trucks_percent(dAADT)
        # Vehicle Utilization
        dUtilization = self.compute_vehicle_utilization(dAADT, dLength)

        ########################
        # Output variables
        ########################
        sRoadCode = np.empty((13, 20), dtype="<U30")  # alternatives, years
        dCondIRI = np.zeros((13, 20), dtype=np.float64)  # alternatives, years
        dCondCON = np.zeros((13, 20), dtype=np.int16)  # alternatives, years
        dCondSNC = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        iCondAge = np.zeros((13, 20), dtype=np.int16)  # ' alternatives, years
        iCondLanes = np.zeros((13, 20), dtype=np.int16)  # ' alternatives, years
        dCondWidth = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dCondLength = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        iCondSurface = np.zeros((13, 20), dtype=np.int16)  # ' alternatives, years
        dCostCapitalFin = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dCostRepairFin = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dCostRecurrentFin = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dCostAgencyFin = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dCostCapitalEco = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dCostRepairEco = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dCostRecurrentEco = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dCostAgencyEco = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dCostVOC = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dCostTime = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dCostUsers = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dCondSpeed = np.zeros((13, 20, 12), dtype=np.float64)  # uble  ' alterntive, years, vehicles
        dCondSpeedAve = np.zeros((13, 20), dtype=np.float64)  # ' alternative, year
        dCostTotal = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dNetTotal = np.zeros((13, 20), dtype=np.float64)  # ' alternatives, years
        dSolIRR = np.zeros((13,), dtype=np.float64)  # As Double '  alternatives
        dSolNPV = np.zeros((13,), dtype=np.float64)  # As Double ' altertnatives
        dSolNPVKm = np.zeros((13,), dtype=np.float64)  # As Double ' alternatives
        dSolNPVCost = np.zeros((13,), dtype=np.float64)  # As Double ' alternatives
        sSolClass = np.empty((13,), dtype="<U30")  # As String ' alternatives
        sSolCode = np.empty((13,), dtype="<U30")  # As String ' alternatives
        sSolName = np.empty((13,), dtype="<U30")  # As String ' alternatives
        dSolCost = np.zeros((13,), dtype=np.float64)  # As Double ' alternatives
        dSolCostkm = np.zeros((13,), dtype=np.float64)  # As Double ' alternatives
        iSolYear = np.zeros((13,), dtype=np.float64)  # As Double ' alternatives

        ####################################################
        # Loop alternatives
        ####################################################
        iTheSelected = 1
        dNPVMax = 0.0

        for ia in range(iNoAlernatives):
            """
            LOOP YEARS
            """
            dYearRoughness = dRoughness
            dYearSNC = dStructuralNo
            iYearAge = iPavementAge
            iYearLanes = iLanes
            dYearWidth = dWidth
            dYearLength = dLength
            iYearSurface = iSurfaceType

            iTheWork = int(dAlternatives[ia, 0])
            iTheYear = int(dAlternatives[ia, 1])
            iTheRepair = self.dRoadWorks[iTheWork - 1, 13]
            iTheRepairY1 = iTheYear + self.dRoadWorks[iTheWork - 1, 14]
            iTheRepairY2 = iTheRepairY1 + self.dRoadWorks[iTheWork - 1, 14]
            iTheRepairY3 = iTheRepairY2 + self.dRoadWorks[iTheWork - 1, 14]
            iTheRepairY4 = iTheRepairY3 + self.dRoadWorks[iTheWork - 1, 14]

            dSolNPV[ia] = 0

            for iy in range(20):
                # lane, width, length
                iCondLanes[ia, iy] = iYearLanes
                dCondWidth[ia, iy] = dYearWidth
                dCondLength[ia, iy] = dYearLength
                dCondSNC[ia, iy] = dYearSNC
                iCondSurface[ia, iy] = iYearSurface

                # Capital Road Work
                if iy == iTheYear - 1:
                    # Look at the Number of Lane Classes
                    if self.dRoadWorks[iTheWork - 1, 7] is not None and self.dRoadWorks[iTheWork - 1, 7] > 0:
                        iCondLanes[ia, iy] = self.dRoadWorks[iTheWork - 1, 7]
                        dCondWidth[ia, iy] = self.dRoadWorks[iTheWork - 1, 8]
                        iCondSurface[ia, iy] = self.dRoadWorks[iTheWork - 1, 9]
                        iYearLanes = self.dRoadWorks[iTheWork - 1, 7]
                        dYearWidth = self.dRoadWorks[iTheWork, 8]
                        iYearSurface = self.dRoadWorks[iTheWork, 9]

                    # Srtructural number after periodic maintenance for bituminous roads
                    if self.dRoadWorks[iTheWork - 1, 10] is not None and self.dRoadWorks[iTheWork - 1, 10] > 0:
                        dCondSNC[ia, iy] = (
                            dCondSNC[ia, iy]
                            + self.dRoadWorks[iTheWork - 1, 10] * self.dRoadWorks[iTheWork - 1, 11] * 0.0393701
                        )
                        dYearSNC = dCondSNC[ia, iy]

                    # Structural number after rehabiliation for bituminous roads
                    if self.dRoadWorks[iTheWork - 1, 12] is not None and self.dRoadWorks[iTheWork - 1, 12] > 0:
                        dCondSNC[ia, iy] = self.dRoadWorks[iTheWork - 1, 12]
                        dYearSNC = dCondSNC[ia, iy]

                    # Capital work costs
                    if iTerrain == 1:
                        dCostCapitalFin[ia, iy] = (
                            self.dRoadWorks[iTheWork - 1, 3]
                            * dCondLength[ia, iy]
                            * dCondWidth[ia, iy]
                            / 1000.0
                            * dCostFactor
                        )
                        dCostCapitalEco[ia, iy] = (
                            self.dRoadWorks[iTheWork - 1, 3]
                            * dCondLength[ia, iy]
                            * dCondWidth[ia, iy]
                            * self.dEconomic_Factor
                            / 1000.0
                            * dCostFactor
                        )
                    elif iTerrain == 2:
                        dCostCapitalFin[ia, iy] = (
                            self.dRoadWorks[iTheWork - 1, 4]
                            * dCondLength[ia, iy]
                            * dCondWidth[ia, iy]
                            / 1000.0
                            * dCostFactor
                        )
                        dCostCapitalEco[ia, iy] = (
                            self.dRoadWorks[iTheWork - 1, 4]
                            * dCondLength[ia, iy]
                            * dCondWidth[ia, iy]
                            * self.dEconomic_Factor
                            / 1000.0
                            * dCostFactor
                        )
                    elif iTerrain == 3:
                        dCostCapitalFin[ia, iy] = (
                            self.dRoadWorks[iTheWork - 1, 5]
                            * dCondLength[ia, iy]
                            * dCondWidth[ia, iy]
                            / 1000.0
                            * dCostFactor
                        )
                        dCostCapitalEco[ia, iy] = (
                            self.dRoadWorks[iTheWork - 1, 5]
                            * dCondLength[ia, iy]
                            * dCondWidth[ia, iy]
                            * self.dEconomic_Factor
                            / 1000.0
                            * dCostFactor
                        )
                    sRoadCode[ia, iy] = self.dRoadWorks[iTheWork - 1, 1]
                    sSolName[ia] = self.dRoadWorks[iTheWork - 1, 0]
                    sSolCode[ia] = self.dRoadWorks[iTheWork - 1, 1]
                    sSolClass[ia] = self.dRoadWorks[iTheWork - 1, 2]
                    iSolYear[ia] = iy + 1  # Since iy is counted from 0 and year order starts from 1
                    dSolCost[ia] = dCostCapitalFin[ia, iy]
                    dSolCostkm[ia] = dSolCost[ia] / dCondLength[ia, iy]

                # repair road work
                if (
                    (iy == iTheRepairY1 - 1)
                    or (iy == iTheRepairY2 - 1)
                    or (iy == iTheRepairY3 - 1)
                    or (iy == iTheRepairY4 - 1)
                ):
                    sRoadCode[ia, iy] = self.dRoadWorks[iTheRepair - 1, 1]
                    if self.dRoadWorks[iTheRepair - 1, 7] is not None and self.dRoadWorks[iTheRepair - 1, 7] > 0:
                        iCondLanes[ia, iy] = self.dRoadWorks[iTheRepair - 1, 7]
                        dCondWidth[ia, iy] = self.dRoadWorks[iTheRepair - 1, 8]
                        iCondSurface[ia, iy] = self.dRoadWorks[iTheRepair - 1, 9]
                        iYearLanes = self.dRoadWorks[iTheRepair, 7]
                        dYearWidth = self.dRoadWorks[iTheRepair, 8]
                        iYearSurface = self.dRoadWorks[iTheRepair, 9]

                    # structural number
                    if self.dRoadWorks[iTheRepair - 1, 12] is not None and self.dRoadWorks[iTheRepair - 1, 12] > 0:
                        dCondSNC[ia, iy] = self.dRoadWorks[iTheRepair - 1, 12]
                        dYearSNC = self.dRoadWorks[iTheRepair - 1, 12]

                    # repair work costs
                    if iTerrain == 1:
                        dCostRepairFin[ia, iy] = (
                            self.dRoadWorks[iTheRepair - 1, 3] * dCondLength[ia, iy] * dCondWidth[ia, iy] / 1000.0
                        )
                        dCostRepairEco[ia, iy] = (
                            self.dRoadWorks[iTheRepair - 1, 3]
                            * dCondLength[ia, iy]
                            * dCondWidth[ia, iy]
                            * self.dEconomic_Factor
                            / 1000.0
                        )
                    elif iTerrain == 2:
                        dCostRepairFin[ia, iy] = (
                            self.dRoadWorks[iTheRepair - 1, 4] * dCondLength[ia, iy] * dCondWidth[ia, iy] / 1000.0
                        )
                        dCostRepairEco[ia, iy] = (
                            self.dRoadWorks[iTheRepair - 1, 4]
                            * dCondLength[ia, iy]
                            * dCondWidth[ia, iy]
                            * self.dEconomic_Factor
                            / 1000.0
                        )
                    elif iTerrain == 3:
                        dCostRepairFin[ia, iy] = (
                            self.dRoadWorks[iTheRepair - 1, 5] * dCondLength[ia, iy] * dCondWidth[ia, iy] / 1000.0
                        )
                        dCostRepairEco[ia, iy] = (
                            self.dRoadWorks[iTheRepair - 1, 5]
                            * dCondLength[ia, iy]
                            * dCondWidth[ia, iy]
                            * self.dEconomic_Factor
                            / 1000.0
                        )

                # recurrent road work without recurrent maintenance condition multipliers
                dCostRecurrentFin[ia, iy] = (
                    self.dRecurrent[iCondSurface[ia, iy] - 1, iCondLanes[ia, iy] - 1] * dCondLength[ia, iy] / 1000000.0
                )
                dCostRecurrentEco[ia, iy] = (
                    self.dRecurrent[iCondSurface[ia, iy] - 1, iCondLanes[ia, iy] - 1]
                    * dCondLength[ia, iy]
                    * self.dEconomic_Factor
                    / 1000000.0
                )

                # Rouhgness
                if iy > 0:
                    dYearRoughness = self.calculate_next_year_roughness(
                        dYearRoughness, iYearAge, ia, iy, iTemperature, iMoisture, dCondSNC, dESATotal, iCondSurface
                    )
                    dYearRoughness = min(16, dYearRoughness)

                iYearAge = iYearAge + 1

                if iy == iTheYear - 1:
                    """
                    Rougnesss effect function of road work type
                    """
                    dYearRoughness = self.dRoadWorks[iTheWork - 1, 6]
                    iYearAge = 1

                if (
                    (iy == iTheRepairY1 - 1)
                    or (iy == iTheRepairY2 - 1)
                    or (iy == iTheRepairY3 - 1)
                    or (iy == iTheRepairY4 - 1)
                ):
                    dYearRoughness = self.dRoadWorks[iTheRepair - 1, 6]
                    iYearAge = 1

                dCondIRI[ia, iy] = dYearRoughness
                iCondAge[ia, iy] = iYearAge

                # VOC
                dCostVOC[ia, iy] = 0
                for iv in range(12):  # 12 types of vehicles
                    if self.dVOC[iCondLanes[ia, iy] - 1, iTerrain - 1, 0, iv] != float(0):
                        dCostVOC[ia, iy] = (
                            dCostVOC[ia, iy]
                            + (
                                self.dVOC[iCondLanes[ia, iy] - 1, iTerrain - 1, 0, iv]
                                + (self.dVOC[iCondLanes[ia, iy] - 1, iTerrain - 1, 1, iv] * dCondIRI[ia, iy])
                                + (
                                    self.dVOC[iCondLanes[ia, iy] - 1, iTerrain - 1, 2, iv]
                                    * np.power(dCondIRI[ia, iy], 2)
                                )
                                + (
                                    self.dVOC[iCondLanes[ia, iy] - 1, iTerrain - 1, 3, iv]
                                    * np.power(dCondIRI[ia, iy], 3)
                                )
                            )
                            * dAADT[iv, iy]
                        )
                dCostVOC[ia, iy] = dCostVOC[ia, iy] * dCondLength[ia, iy] * 365 / 1000000

                # Speed
                dCondSpeedAve[ia, iy] = 0
                ii = 0
                for iv in range(0, 12):
                    if self.dSPEED[iCondLanes[ia, iy] - 1, iTerrain - 1, 0, iv] != float(0):
                        dCondSpeed[ia, iy, iv] = (
                            self.dSPEED[iCondLanes[ia, iy] - 1, iTerrain - 1, 0, iv]
                            + (self.dSPEED[iCondLanes[ia, iy] - 1, iTerrain - 1, 1, iv] * dCondIRI[ia, iy])
                            + (self.dSPEED[iCondLanes[ia, iy] - 1, iTerrain - 1, 2, iv] * np.power(dCondIRI[ia, iy], 2))
                            + (self.dSPEED[iCondLanes[ia, iy] - 1, iTerrain - 1, 3, iv] * np.power(dCondIRI[ia, iy], 3))
                        )

                        dCondSpeedAve[ia, iy] = dCondSpeedAve[ia, iy] + dCondSpeed[ia, iy, iv]
                        ii = ii + 1

                dCondSpeedAve[ia, iy] = dCondSpeedAve[ia, iy] / ii

                # Time
                dCostTime[ia, iy] = 0
                for iv in range(12):
                    if dCondSpeed[ia, iy, iv] > float(0):
                        dCostTime[ia, iy] = (
                            dCostTime[ia, iy]
                            + 1
                            / dCondSpeed[ia, iy, iv]
                            * dCondLength[ia, iy]
                            * self.dVehicleFleet[iv, 1]
                            * self.dVehicleFleet[iv, 2]
                            * dAADT[iv, iy]
                            * 365
                            / 1000000
                        )

                # Pavement Condition Class function of rougness
                dCondCON[ia, iy] = get_cc_from_iri(self.iri_cc_df, dCondIRI[ia, iy], iSurfaceType)
                dCostRecurrentFin[ia, iy] = dCostRecurrentFin[ia, iy] * dRecMult[dCondCON[ia, iy] - 1]
                dCostRecurrentEco[ia, iy] = dCostRecurrentEco[ia, iy] * dRecMult[dCondCON[ia, iy] - 1]

                # road agency costs
                dCostAgencyFin[ia, iy] = dCostCapitalFin[ia, iy] + dCostRepairFin[ia, iy] + dCostRecurrentFin[ia, iy]
                dCostAgencyEco[ia, iy] = dCostCapitalEco[ia, iy] + dCostRepairEco[ia, iy] + dCostRecurrentEco[ia, iy]

                # Users and Total
                dCostUsers[ia, iy] = dCostVOC[ia, iy] + dCostTime[ia, iy]
                dCostTotal[ia, iy] = dCostAgencyEco[ia, iy] + dCostUsers[ia, iy]

                # Net Benefits
                dNetTotal[ia, iy] = dCostTotal[0, iy] - dCostTotal[ia, iy]

                # NPV
                # Serious Note: raise to the power iy not (iy - 1) in the following equation
                dSolNPV[ia] = dSolNPV[ia] + dNetTotal[ia, iy] / ((1 + self.dDiscount_Rate) ** (iy))
                dSolNPVKm[ia] = dSolNPV[ia] / dCondLength[ia, 0]

                if dSolCost[ia] > 0:
                    dSolNPVCost[ia] = dSolNPV[ia] / dSolCost[ia]
                else:
                    dSolNPVCost[ia] = 0
            # End loop iy

            if ia > 1:
                # add computation of IRR here if needed
                dSolIRR[ia] = 0

            if dSolNPV[ia] >= dNPVMax:
                iTheSelected = ia
                dNPVMax = dSolNPV[ia]

        # print out values by year
        def pyear(desc, x):
            print(f"======================\n{desc}\n======================")
            for i in range(0, 20):
                print(f"{i: >2}  {x[i]: 0.3}")

        # pyear("iri_base", dCondIRI[0])

        ###########################################################
        # Get the output results
        ###########################################################
        results = {
            "work_class": sSolClass[iTheSelected],
            "work_type": sSolCode[iTheSelected],
            "work_name": sSolName[iTheSelected],
            "work_cost": dSolCost[iTheSelected],
            "work_cost_km": dSolCostkm[iTheSelected],
            "work_year": int(iSolYear[iTheSelected]),
            "npv": dSolNPV[iTheSelected],
            "npv_km": dSolNPVKm[iTheSelected],
            "npv_cost": dSolNPVCost[iTheSelected],
            "eirr": dSolIRR[iTheSelected],
            "aadt": dAADT[12].tolist(),
            "truck_percent": dTRucks,
            "vehicle_utilization": dUtilization,
            "esa_loading": dESATotal[1],
            "iri_projection": dCondIRI[iTheSelected].tolist(),
            "iri_base": dCondIRI[0][0:10].tolist(),
            "con_projection": dCondCON[iTheSelected].tolist(),
            "con_base": dCondCON[0].tolist(),
            "financial_recurrent_cost": dCostRecurrentFin[iTheSelected].tolist(),
            "net_benefits": dNetTotal[iTheSelected].tolist(),
        }
        return CbaResult(results)

    # JC: I'm not sure what this does, but it's used in a number of places to get the left index
    #     into the dWorkEvaluated member variable
    def get_left_index(self, iSurfaceType, iRoadClass, iConditionClass):
        return (iSurfaceType - 1) * 50 + (iRoadClass - 1) * 5 + iConditionClass - 1

    def compute_alternatives(self, iSurfaceType, iRoadClass, iConditionClass):
        iNoAlernatives = 0
        dAlternatives = np.zeros((13, 2), dtype=np.float64)

        # Get initial road work for the 13 alternatives
        left_index = self.get_left_index(iSurfaceType, iRoadClass, iConditionClass)
        dAlternatives[0, 0] = int(self.dWorkEvaluated[left_index, 1])
        dAlternatives[1:7, 0] = int(self.dWorkEvaluated[left_index, 2])
        dAlternatives[7:13, 0] = int(self.dWorkEvaluated[left_index, 3])

        # Define years of initial works for 13 alternatives
        dAlternatives[0, 1] = int(self.dWorkEvaluated[left_index, 0])

        if dAlternatives[1, 0] > 0:  # first road work defined: evaluate at least 7 alternatives
            dAlternatives[1:7, 1] = [1, 2, 3, 4, 5, 6]
            iNoAlernatives = 7

        if dAlternatives[7, 0] > 0:  # second road work defined: evaluate 13 alternatives
            dAlternatives[7:13, 1] = [1, 2, 3, 4, 5, 6]
            iNoAlernatives = 13

        if dAlternatives[1, 0] == 0 and dAlternatives[7, 0] == 0:  # no road works defined: evaluate 2 base alternatives
            dAlternatives[1, 0] = self.dWorkEvaluated[left_index, 1]
            dAlternatives[1, 1] = self.dWorkEvaluated[left_index, 0]
            iNoAlernatives = 2

        return iNoAlernatives, dAlternatives

    def compute_cost_factor(self, iSurfaceType, iRoadClass, iConditionClass):
        baz = iConditionClass - 1
        return self.dWorkEvaluated[(iSurfaceType - 1) * 50 + (iRoadClass - 1) * 5 + baz, 4]

    def calculate_next_year_roughness(
        self, dYearRoughness, iYearAge, ia, iy, iTemperature, iMoisture, dCondSNC, dESATotal, iCondSurface
    ):
        """
        Rougnesss progression function of surface type
        """

        surface_condition = iCondSurface[ia, iy]
        foo, const, Kgp, Kgm, a0, a1, a2 = self.dRoadDet[surface_condition - 1, 0:7]

        # Surface condition classes 1,4,5,6,7 always use constant deterioration factors
        # classes 2 & 3 use them when the FOO is 1
        if surface_condition in (1, 4, 5, 6, 7) or foo == float(1):
            return dYearRoughness * (1 + const)

        # otherwise the surface_condition is either 2 or 3
        moisture_coeff = self.dm_coeff[iTemperature - 1, iMoisture - 1]

        if foo == float(3):  # Climate Related Only
            return dYearRoughness * (1 + moisture_coeff)

        if foo == float(2):
            # HDM-4 Simplified Equation:
            # RIb = RIa + Kgp * (a0 * Exp (Kgm * m * AGE3) * [(1 + SNC * a1)]-5 * YE4 + a2 * AGE3) + (Kgm *m * RIa)
            snc = dCondSNC[ia, iy]
            ye4 = dESATotal[iy]
            return dYearRoughness + (
                Kgp
                * (a0 * np.exp(Kgm * moisture_coeff * iYearAge) * np.power((1 + snc * a1), -5) * ye4 + a2 * iYearAge)
                + (Kgm * moisture_coeff * dYearRoughness)
            )

    def compute_annual_traffic(self, dAADT, iGrowthScenario):
        for iv in range(12):
            for iy in range(1, 20):
                dAADT[iv, iy] = dAADT[iv, iy - 1] * (1 + self.dGrowth[iGrowthScenario - 1, iv])

        for iy in range(1, 20):
            dAADT[12, iy] = 0
            for iv in range(12):
                dAADT[12, iy] = dAADT[12, iy] + dAADT[iv, iy]

        return dAADT

    def compute_esa_loading(self, dAADT, iLanes):
        dESATotal = np.zeros((20,), dtype=np.float64)

        for iy in range(0, 20):
            dESATotal[iy] = 0
            for iv in range(0, 12):
                dESATotal[iy] = (
                    dESATotal[iy]
                    + dAADT[iv, iy] * self.dVehicleFleet[iv, 0] / 1000000 * 365 / self.dWidthDefaults[iLanes - 1, 1]
                )

        return dESATotal

    def compute_trucks_percent(self, dAADT):
        return (dAADT[5, 0] + dAADT[6, 0] + dAADT[7, 0] + dAADT[8, 0]) / dAADT[12, 0]

    def compute_vehicle_utilization(self, dAADT, dLength):
        dUtilization = 0
        for iv in range(0, 12):
            dUtilization = dUtilization + dAADT[iv, 0] * dLength * 365 / 1000000
        return dUtilization

    def get_initial_roughness(self, section):
        if section.roughness == 0 and section.condition_class == 0:
            raise ValueError("Must define either roughness or road condition class")
        if section.roughness > 0:
            return section.roughness
        roughness, pavementAge = dConditionData[section.surface_type - 1, section.condition_class - 1]
        print(roughness, pavementAge)
        return roughness
