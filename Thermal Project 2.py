# -*- coding: utf-8 -*-
"""
Created on Sat Nov  3 12:11:13 2018

@author: kpett
"""
import matplotlib.pyplot as plt
import cantera as ct
  
def h_OutPump(n_pump, h_OutIs, h_In):
    h_OutAct = ((h_OutIs - h_In)/n_comp)+h_In
    return h_OutAct

def h_OutCompressor(n_comp, h_OutIs, h_In):
    h_OutAct = ((h_OutIs - h_In)/n_comp)+h_In
    return h_OutAct

def h_OutTurbine(n_turb, h_OutIs, h_In):
    h_OutAct = -(n_turb)*(h_In-h_OutIs)+h_In
    return h_OutAct

def atm2Pa(P):
    P = P * 101325
    return P

mr = []
cst = []
ben = []
n_cc = []
prs = []
mdots = []

#Define Fluid States
airCompIn = ct.Nitrogen()
airCompOut = ct.Nitrogen()
airTurbIn = ct.Nitrogen()
airTurbOut = ct.Nitrogen()
airHrsgOut = ct.Nitrogen()
waterPumpIn = ct.Water()
waterPumpOut = ct.Water()
waterTurbIn = ct.Water()
waterTurbOut = ct.Water()

#Define Efficiencies
n_comp = 0.8
n_turb_a = 0.85
n_Hrsg = 0.86
n_pump = 0.9
n_turb_w = 0.9

for pr in range(3,20):
    cost = 0    #cost per air mass flow rate
    benefit = 0     #benefit per air mass flow rate
    
    "State 5 - AIR - Inlet to Compressor"
    airPressCompIn = atm2Pa(1)
    airTempCompIn = 300             
    airCompIn.TP = airTempCompIn, airPressCompIn    
    airEntropyCompIn = airCompIn.entropy_mass
    airEnthalpyCompIn = airCompIn.enthalpy_mass
    
    "State 6 - AIR - Outlet of Compressor/Inlet to Combustion Chamber"
    airPressCompOut = atm2Pa(1*pr)
    airIsEntropyCompOut = airEntropyCompIn
    airCompOut.SP = airIsEntropyCompOut, airPressCompOut
    airIsEnthalpyCompOut= airCompOut.enthalpy_mass
    airEnthalpyCompOut = h_OutCompressor(n_comp, airIsEnthalpyCompOut,airEnthalpyCompIn)
    airCompOut.HP = airEnthalpyCompOut,airPressCompOut
    
    cost = cost + (airIsEnthalpyCompOut-airEnthalpyCompIn)
    
    "State 7 - AIR - Outlet of Combustion Chamber/Inlet to Turbine"    
    airPressTurbIn = airPressCompOut
    airTempTurbIn = 1400
    airTurbIn.TP = airTempTurbIn,airPressTurbIn
    airEntropyTurbIn = airTurbIn.entropy_mass
    airEnthalpyTurbIn = airTurbIn.enthalpy_mass
    
    cost = cost + (airEnthalpyTurbIn-airEnthalpyCompOut)
    
    "State 8 - AIR - Outlet of Turbine/Inlet to HRSG"
    airPressTurbOut = airPressCompIn
    airIsEntropyTurbOut = airEntropyTurbIn
    airTurbOut.SP = airIsEntropyTurbOut, airPressTurbOut
    airIsEnthalpyTurbOut = airTurbOut.enthalpy_mass
    airEnthalpyTurbOut = h_OutTurbine(n_turb_a, airIsEnthalpyTurbOut, airEnthalpyTurbIn)
    airTurbOut.HP = airEnthalpyTurbOut,airPressTurbOut
    
    benefit = benefit + (airEnthalpyTurbIn-airEnthalpyTurbOut)
    
    "State 9 - AIR - Outlet of HRSG"
    airTempHrsgOut = 450
    airPressHrsgOut = airPressTurbOut
    airHrsgOut.TP = airTempHrsgOut, airPressHrsgOut
    airEnthalpyHrsgOut = airHrsgOut.enthalpy_mass
        
    "State 1 - WATER - Outlet of Condenser/Inlet to pump"
    waterPressPumpIn = 5*10**3
    waterPumpIn.PX = waterPressPumpIn, 0
    waterEnthalpyPumpIn = waterPumpIn.enthalpy_mass
    waterEntropyPumpIn = waterPumpIn.entropy_mass
    
    "State 2 - WATER - Outlet of Pump/Inlet to HRSG"
    waterPressPumpOut = 70*10**6
    waterIsEntropyPumpOut = waterEntropyPumpIn
    waterPumpOut.SP = waterIsEntropyPumpOut, waterPressPumpOut
    waterIsEnthalpyPumpOut = waterPumpOut.enthalpy_mass
    waterEnthalpyPumpOut = h_OutPump(n_pump, waterIsEnthalpyPumpOut, waterEnthalpyPumpIn)
    waterPumpOut.HP = waterEnthalpyPumpOut,waterPressPumpOut
    
    "State 3 - WATER - Outlet of HRSG/Inlet to Turbine"
    waterPressTurbIn = waterPressPumpOut
    waterPerfTempTurbIn = 450                                 #this may  be the wrong method
    waterTurbIn.TP = waterPerfTempTurbIn, waterPressTurbIn
    waterPerfEnthalpyTurbIn = waterTurbIn.enthalpy_mass
    mPerfDotRatio = (airEnthalpyTurbOut-airEnthalpyHrsgOut)/(waterPerfEnthalpyTurbIn-waterEnthalpyPumpOut)
    mDotRatio = n_Hrsg*mPerfDotRatio 
    waterEnthalpyTurbIn = ((airEnthalpyTurbOut-airEnthalpyHrsgOut)/(mDotRatio))+(waterEnthalpyPumpOut)
    waterTurbIn.HP = waterEnthalpyTurbIn,waterPressTurbIn 
    waterEntropyTurbIn = waterTurbIn.entropy_mass
    
    cost = cost + mDotRatio*(waterIsEnthalpyPumpOut-waterEnthalpyPumpIn)
    
    "State 4 -WATER - Outlet of Turbine/Inlet to Condenser"
    waterPressTurbOut = waterPressPumpIn
    waterIsEntropyTurbOut =  waterEntropyTurbIn
    waterTurbOut.SP = waterIsEntropyTurbOut,waterPressTurbOut
    waterIsEnthalpyTurbOut = waterTurbOut.enthalpy_mass
    waterEnthalpyTurbOut = h_OutTurbine(n_turb_w, waterIsEnthalpyTurbOut, waterEnthalpyTurbIn)
    waterTurbOut.HP =  waterEnthalpyTurbOut, waterPressTurbOut
    
    benefit = benefit + mDotRatio*(waterEnthalpyTurbIn-waterEnthalpyTurbOut)
    
    inss = cost + airEnthalpyCompIn 
    outss = benefit + airEnthalpyHrsgOut + mDotRatio*(waterEnthalpyPumpIn-waterEnthalpyTurbOut) #missing entropy values
    
    #Arrays
    cst.append(cost)
    ben.append(benefit)
    mr.append(mDotRatio)
    n_cc.append(benefit/cost)
    prs.append(pr)
    mdots.append(mDotRatio)
    
#fig = plt.figure(figsize=(10, 10))
#sub1 = fig.add_subplot(221) # instead of plt.subplot(2, 2, 1)
#sub1.set_title('CoGen Cycle Efficiency') # non OOP: plt.title('The function f')
#sub1.plot(prs, n_cc)
#sub2 = fig.add_subplot(222)
#sub2.set_title('Mass Flow Ratios')
#sub2.plot(prs, mdots)
#sub3 = fig.add_subplot(223)
#sub3.set_title('Net Output')
#sub3.plot(prs, ben)
#plt.tight_layout()
#plt.show()
fig, ax1 = plt.subplots()
ax1.plot(prs, ben, lw=2, color="blue")
ax1.set_ylabel(r"Net Power per Air Mass Flow Rate $(J/kg)$", fontsize=16, color="blue")
for label in ax1.get_yticklabels():
    label.set_color("blue")
    
ax2 = ax1.twinx()
ax2.plot(prs, n_cc, lw=2, color="red")
ax2.set_ylabel(r"Thermal Efficiency $()$", fontsize=16, color="red")
for label in ax2.get_yticklabels():
    label.set_color("red")