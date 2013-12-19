
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%% initialization %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

load DataProfile

% create objects
utility = Obj_Utility;
ObjLimit = Obj_TechLimit;
ObjRate = Obj_RateClass;
vec_ObjExpense = Obj_UtilityExpense;
vec_ObjRateComponent = Obj_RateComponent;
vec_ObjCustDetached = Obj_CustomerGroup;
vec_ObjCustAttached = Obj_CustomerGroup;
ObjPv = Obj_PV;
for i = 1:1
    vec_ObjExpense(i) = Obj_UtilityExpense;
    vec_ObjRateComponent(1,i) = Obj_RateComponent;
end
for i = 1:20
    vec_ObjCustDetached(i) = Obj_CustomerGroup; 
    vec_ObjCustAttached(i) = Obj_CustomerGroup;
end

% technical potential of grid
ObjLimit.A = 200;
ObjLimit.B = 2.5;
ObjLimit.C = 1;
ObjLimit.Limit = 0.20;

% utility base load
utility.vec_BaseHourlyDemand = zeros(8760,1);
for i = 3:9
    utility.vec_BaseHourlyDemand = utility.vec_BaseHourlyDemand + ...
        reshape(LoadProfile(i).prof',8760,1)*(LoadProfile(i).sales/LoadProfile(i).total);
end
utility.vec_BaseHourlyGeneration = reshape(LoadProfile(10).prof',8760,1);
utility.vec_BaseYearlyGeneration = (38650369/1330199364)*(1e6*1300)*interp1(0:2:24,[0 0.4 1.0 2.1 3.6 5.0 7.5 10.0 16.0 21.0 27.3 34.3 41.2],0:24);
utility.vec_BaseHourlyDemand = zeros(8760,1);
utility.vec_BaseYearlyGeneration = zeros(8760,1);
utility.RatePolicy = RatePolicy;
utility.ExoRates = ExoRates;

% initialize rate class
utility.vec_RateClass = ObjRate;
ObjRate.Name = 'Residential';
ObjRate.vec_RateComponent = Obj_RateComponent;
for i = 1:1
    ObjRate.vec_RateComponent(i) = vec_ObjRateComponent(1,i);
end
ObjRate.vec_CustomerGroup = Obj_CustomerGroup;
for i = 1:20
    ObjRate.vec_CustomerGroup(i) = vec_ObjCustDetached(i);
    ObjRate.vec_CustomerGroup(i+20) = vec_ObjCustAttached(i);
end
ObjRate.vec_RateComponent(1).BaselineSummer = 12.26;
ObjRate.vec_RateComponent(1).BaselineWinter = 10.11;

% utility expenses
utility.vec_UtilityExpense = Obj_UtilityExpense;
for i = 1:1
    utility.vec_UtilityExpense(i) = vec_ObjExpense(i);
end
vec_ObjExpense(1).Name = 'Generation Operating';
vec_ObjExpense(1).InvestmentFlag = 0;
vec_ObjExpense(1).vec_OperatingFixed =   2.580065606616279e9*[1 (1+DistInc/100).^(1:30)];
vec_ObjExpense(1).vec_OperatingVariable = 0.08205*ones(8760,1);
vec_ObjExpense(1).CostDriver = 1;
%vec_ObjExpense(1).OpGrowthRate = 0.0;

% initialize rate components
vec_ObjRateComponent(1,1).Name = 'Generation Operating';
vec_ObjRateComponent(1,1).ComponentType = 1;
vec_ObjRateComponent(1,1).Schedule = [ [0;1;1.3;2;3] [(0.04985+0.08205)/(1.01); (0.07899+0.08205)/(1.01); 0.16189+0.08205; 0.19689+0.08205; 0.23189+0.08205]];
%vec_ObjRateComponent(1,1).Schedule = [ [0;1;1.3;2;3] [(0.04985+0.08205)/(1.0); (0.07899+0.08205)/(1.0); 0.16189+0.08205; 0.19689+0.08205; 0.23189+0.08205]];
vec_ObjRateComponent(1,1).CustomerCharge = 0;
vec_ObjRateComponent(1,1).ExcessPrice = 0.0350;

% initialize customer groups
X = [ 152825 514066 599871 650102 538394 ...
      413408 346548 194827 170615 88875 ...
      117678 55506 49652 52475 29767 ...
      8743 10383 8649 14959 8630]';
MF = round([(1:-0.25:0.1)'; 0.10*ones(6,1); 0.05*ones(10,1)].*X);
SF = X - MF;
SFrental = round(0.19*SF);
SFowned = SF - SFrental;
SFshaded = round(0.35*SFowned);
SF = SFowned - SFshaded;

YearlyPv = 1514;
TotalResDetached = sum(X-MF-SFrental - SFshaded);
vec_CustDetachedDist = X-MF-SFrental - SFshaded;  
vec_SolarGeneration = [0 2:0.2:10];
for i = 1:20
vec_ObjCustDetached(i).Name = ['Residential Detached ' num2str(i*100)];
vec_ObjCustDetached(i).M = SF(i);
vec_ObjCustDetached(i).arr_CustomerState = Obj_CustomerState;
vec_ObjCustDetached(i).MinGeneration = 1*YearlyPv;
vec_ObjCustDetached(i).MaxGeneration = min(10*YearlyPv,i*100*12);
vec_ObjCustDetached(i).Consumption = i*100*12;
for j = 1:length(vec_SolarGeneration)
    vec_ObjCustDetached(i).arr_CustomerState(j) = Obj_CustomerState;
    vec_ObjCustDetached(i).arr_CustomerState(j).State = 0;
    vec_ObjCustDetached(i).arr_CustomerState(j).vec_StateIncTime = zeros(1,100);
    vec_ObjCustDetached(i).arr_CustomerState(j).YearlyConsumption = i*100*12;
    vec_ObjCustDetached(i).arr_CustomerState(j).YearlySolarGeneration = vec_SolarGeneration(j)*YearlyPv;
    vec_ObjCustDetached(i).arr_CustomerState(j).func_InitConsumption(reshape(LoadProfile(1).prof'*(i*100*12/LoadProfile(1).total),8760,1))
    vec_ObjCustDetached(i).arr_CustomerState(j).func_InitGeneration(reshape(LoadProfile(10).prof',8760,1));
    vec_ObjCustDetached(i).arr_CustomerState(j).func_InitAggregate();
end
vec_ObjCustDetached(i).arr_CustomerState(1).State = 1;
vec_ObjCustDetached(i).AdoptExt = AdoptExt;
vec_ObjCustDetached(i).AdoptDiff = AdoptDiff;
vec_ObjCustDetached(i).SavingsA = SavingsA;
vec_ObjCustDetached(i).SavingsB = SavingsB;
vec_ObjCustDetached(i).SavingsC = SavingsC;
vec_ObjCustDetached(i).Pv = ObjPv;
vec_ObjCustDetached(i).TechLimit = ObjLimit;
vec_ObjCustDetached(i).AvgSolarBill = 0;
vec_ObjCustDetached(i).InitialBill = Inf;
end
TotalResAttached = sum(MF+SFrental+SFshaded);
for i = 1:20
vec_ObjCustAttached(i).Name = ['Residential Attached ' num2str(i*100)];
vec_ObjCustAttached(i).M = X(i) - SF(i); %MF(i)+SFrental(i) + SFshaded(i);
vec_ObjCustAttached(i).MinGeneration = 0;
vec_ObjCustAttached(i).MaxGeneration = 0;
vec_ObjCustAttached(i).Consumption = i*100*12;
vec_ObjCustAttached(i).arr_CustomerState = Obj_CustomerState;
vec_ObjCustAttached(i).arr_CustomerState(1) = Obj_CustomerState;
vec_ObjCustAttached(i).arr_CustomerState(1).State = 1;
vec_ObjCustAttached(i).arr_CustomerState(1).vec_StateIncTime = zeros(1,100);
vec_ObjCustAttached(i).arr_CustomerState(1).YearlyConsumption = i*100*12;
vec_ObjCustAttached(i).arr_CustomerState(1).YearlySolarGeneration = 0;
vec_ObjCustAttached(i).arr_CustomerState(1).func_InitConsumption(reshape(LoadProfile(1).prof'*(i*100*12/LoadProfile(1).total),8760,1));
vec_ObjCustAttached(i).arr_CustomerState(1).func_InitGeneration(reshape(LoadProfile(10).prof',8760,1));
vec_ObjCustAttached(i).arr_CustomerState(1).func_InitAggregate();
vec_ObjCustAttached(i).TechLimit = ObjLimit;
vec_ObjCustAttached(i).Pv = ObjPv;
vec_ObjCustAttached(i).AvgSolarBill = 0;
vec_ObjCustAttached(i).InitialBill = Inf;
end

% initialize PV
%load DataLCOE.mat
%ObjPv.vec_LevelCost = LCOE(FederalITC,:);

load DataProfile
prof = LoadProfile(10).prof;
clear LoadProfile
CPW = 1000*(7.13 - SolarDecreaseRate*(0:14));
if FederalITC == 1
    CPW(1:5) = 0.7*CPW(1:5);
else
    CPW = 0.7*CPW;
end
r = 0.05;
i = 0.05;
d = 1;
prof = 0.83*prof./1000;
E = sum(sum(prof))*(d.^(0:30));
LCOE = zeros(1,15);
R = (1/(1+r)).^(0:30);
for k=1:15
    C = [0.2*CPW(k) payper(i,20,CPW(k)*0.8)*ones(1,20) zeros(1,10)];
    LCOE(1,k) = sum(C.*R)/(sum(E.*R));
end
ObjPv.vec_LevelCost = LCOE;


