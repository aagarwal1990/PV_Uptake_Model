clear

%% Plot simulation PV uptake

raw_data = csvread('SolarUptakeZipcodeFrom1999.csv',1,1);
total_adoptions = sum(raw_data,1);

M = csvread('output_files_savings_0\output_savings_0_72.txt');
x1 = flipud(M(:,1));
y1 = flipud(M(:,2));
M = csvread('output_files_savings_2500\output_savings_2500_72.txt');
x2 = flipud(M(:,1));
y2 = flipud(M(:,2));
M = csvread('output_files_savings_5000\output_savings_5000_72.txt');
x3 = flipud(M(:,1));
y3 = flipud(M(:,2));
M = csvread('output_files_savings_10000\output_savings_10000_72.txt');
x4 = flipud(M(:,1));
y4 = flipud(M(:,2));
clear M

clf(figure(1))
hold on
plot(x1 + 168,(y1 + 100)*400, 'r', 'linewidth', 2)
plot(x2 + 168,(y2 + 100)*400, 'b', 'linewidth', 2)
plot(x3 + 168,(y3 + 100)*400, 'k', 'linewidth', 2)
plot(x4 + 168,(y4 + 100)*400, 'g', 'linewidth', 2)
plot(1:168, total_adoptions(1:168), 'x')
hold off
legend('Savings $0','Savings $2500','Savings $5000','Savings $10000','Data')
legend('location','northwest')
axis([1 253 0 400000])
ylabel('Number of Adopters')
xlabel('Year')
grid on
box on
set(findall(gcf,'type','text'),'fontsize',14)
set(gca,'fontsize',14)
set(gca,'XTick',13:60:313)
set(gca,'XTickLabel',{'2000','2005','2010','2015','2020','2025'})
set(gca,'YTick',0:100000:1400000)
set(gca,'YTickLabel',{'0',...
    '100000',...
    '200000',...
    '300000',...
    '400000',...
    '500000',...
    '600000',...
    '700000',...
    '800000',...
    '900000',...
    '1000000',...
    '1100000',...
    '1200000',...
    '1300000',...
    '1400000'})

%% Plot impact of feedback

raw_data = csvread('SolarUptakeZipcodeFrom1999.csv',1,1);
total_adoptions = sum(raw_data,1);

M = csvread('output_files_savings_2500\output_savings_2500_72.txt');
x1 = flipud(M(:,1));
y1 = flipud(M(:,2));
M = csvread('output_files_savings_2500\output_savings_2500_72_no_feedback.txt');
x2 = flipud(M(:,1));
y2 = flipud(M(:,2));
M = csvread('output_files_savings_5000\output_savings_5000_72.txt');
x3 = flipud(M(:,1));
y3 = flipud(M(:,2));
M = csvread('output_files_savings_5000\output_savings_5000_72_no_feedback.txt');
x4 = flipud(M(:,1));
y4 = flipud(M(:,2));
clear M

clf(figure(2))
hold on
plot(x1 + 168,(y1 + 100)*400, 'r', 'linewidth', 2)
plot(x2 + 168,(y2 + 100)*400, 'r-.', 'linewidth', 2)
plot(x3 + 168,(y3 + 100)*400, 'k', 'linewidth', 2)
plot(x4 + 168,(y4 + 100)*400, 'k-.', 'linewidth', 2)
plot(1:168, total_adoptions(1:168), 'x')
hold off
legend('Savings $2500','Savings $2500 (no feedback)','Savings $5000','Savings $5000 (no feedback)','Data')
legend('location','northwest')
axis([1 253 0 400000])
ylabel('Number of Adopters')
xlabel('Year')
grid on
box on
set(findall(gcf,'type','text'),'fontsize',14)
set(gca,'fontsize',14)
set(gca,'XTick',13:60:313)
set(gca,'XTickLabel',{'2000','2005','2010','2015','2020','2025'})
set(gca,'YTick',0:100000:1400000)
set(gca,'YTickLabel',{'0',...
    '100000',...
    '200000',...
    '300000',...
    '400000',...
    '500000',...
    '600000',...
    '700000',...
    '800000',...
    '900000',...
    '1000000',...
    '1100000',...
    '1200000',...
    '1300000',...
    '1400000'})

%% Plot adoption by tier

M = csvread('output_files_savings_5000\output_savings_5000_72_adoption_distribution.txt');
clf(figure(3))
bar(100:100:2000,400*M)
xlabel('Average Monthly Consumption')
ylabel('Number of Adopters')
grid on
box on
axis([0 2100 0 25000])
set(findall(gcf,'type','text'),'fontsize',14)
set(gca,'fontsize',14)
set(gca,'XTick',0:500:2100)
set(gca,'XTickLabel',{'0','500','1000','1500','2000'})
set(gca,'YTick',0:5000:25000)
set(gca,'YTickLabel',{'0',...
    '5000',...
    '10000',...
    '15000',...
    '20000',...
    '25000'})
fprintf('<= 700 kWh %d \n',sum(M(1:7))*400)
fprintf('800 and 900 kWh %d \n',sum(M(8:9))*400)
fprintf('>= 1000 kWh %d \n',sum(M(10:20))*400)
