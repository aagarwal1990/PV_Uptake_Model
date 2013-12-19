clear

N = 4200000;
B = fittype('(1-exp(-x*(p+q))) / (1+(q/p)*exp(-x*(p+q)))');

raw_data = csvread('SolarUptakeZipcodeFrom1999.csv',1,1);

%% Fits with different constant market sizes

clf(figure(1))
r = 1:168;
x = 1:312;
%x = 1:168;

fprintf('0.10 * N\n')
total_adoptions = sum(raw_data,1)./(0.10*N);
bass_fit = fit(r',total_adoptions(r)',B,'StartPoint',[1e-07,1e-07],'Lower',[0.0,0.0],'Upper',[1,1])
p = bass_fit.p;
q = bass_fit.q;
y = (1-exp(-x.*(p+q))) ./ (1+(q/p)*exp(-x.*(p+q)));
figure(1)
hold on
plot(x, y*(0.1*N),'k','linewidth',2)
hold off

fprintf('0.20 * N\n')
total_adoptions = sum(raw_data,1)./(0.20*N);
bass_fit = fit(r',total_adoptions(r)',B,'StartPoint',[1e-07,1e-07],'Lower',[0.0,0.0],'Upper',[1,1])
p = bass_fit.p;
q = bass_fit.q;
y = (1-exp(-x.*(p+q))) ./ (1+(q/p)*exp(-x.*(p+q)));
figure(1)
hold on
plot(x, y*(0.2*N),'b','linewidth',2)
hold off

fprintf('0.30 * N\n')
total_adoptions = sum(raw_data,1)./(0.30*N);
bass_fit = fit(r',total_adoptions(r)',B,'StartPoint',[1e-07,1e-07],'Lower',[0.0,0.0],'Upper',[1,1])
p = bass_fit.p;
q = bass_fit.q;
y = (1-exp(-x.*(p+q))) ./ (1+(q/p)*exp(-x.*(p+q)));
figure(1)
hold on
plot(x, y*(0.3*N),'g','linewidth',2)
hold off

fprintf('0.40 * N\n')
total_adoptions = sum(raw_data,1)./(0.40*N);
bass_fit = fit(r',total_adoptions(r)',B,'StartPoint',[1e-07,1e-07],'Lower',[0.0,0.0],'Upper',[1,1])
p = bass_fit.p;
q = bass_fit.q;
y = (1-exp(-x.*(p+q))) ./ (1+(q/p)*exp(-x.*(p+q)));

figure(1)
hold on
plot(x, y*(0.4*N),'r','linewidth',2)
hold off

figure(1)
hold on
r = 1:168;
total_adoptions = sum(raw_data,1);
plot(r, total_adoptions(r), 'bx')
hold off
xlabel('Year')
ylabel('Number of Adopters')
box on
grid on
legend('10%','20%','30%','40%','data')
legend('location','northwest')
%axis([1 193 0 40000])
axis([1 313 0 1400000])
set(findall(gcf,'type','text'),'fontsize',14)
set(gca,'fontsize',14)
set(gca,'XTick',13:60:313)
set(gca,'XTickLabel',{'2000','2005','2010','2015','2020','2025'})
%set(gca,'YTick',0:10000:40000)
%set(gca,'YTickLabel',{'0','10000','20000','30000','40000'})
set(gca,'YTick',0:200000:1400000)
set(gca,'YTickLabel',{'0',...
    '200000',...
    '400000',...
    '600000',...
    '800000',...
    '1000000',...
    '1200000',...
    '1400000'})

%% Fits with expanding market size

S1 = 0.05*N;
S2 = 0.10*N;
S3 = 0.20*N;
S4 = 0.35*N;

total_adoptions = sum(raw_data,1);
total_adoptions(1:7*12) = total_adoptions(1:7*12)./(S1);
total_adoptions(7*12+1:10*12) = total_adoptions(7*12+1:10*12)./(S2);
total_adoptions(10*12+1:13*12) = total_adoptions(10*12+1:13*12)./(S3);
total_adoptions(13*12+1:14*12) = total_adoptions(13*12+1:14*12)./(S4);

r1 = 1:7*12;
r2 = 7*12+1:10*12;
r3 = 10*12+1:13*12;
r4 = 13*12+1:14*12;
bass_fit_1 = fit(r1',total_adoptions(r1)',B,'StartPoint',[1e-07,0.01],'Lower',[0.0,0.0],'Upper',[1,1])
bass_fit_2 = fit(r2',total_adoptions(r2)',B,'StartPoint',[1e-07,0.01],'Lower',[0.0,0.0],'Upper',[1,1])
bass_fit_3 = fit(r3',total_adoptions(r3)',B,'StartPoint',[1e-07,0.01],'Lower',[0.0,0.0],'Upper',[1,1])
bass_fit_4 = fit(r4',total_adoptions(r4)',B,'StartPoint',[1e-07,0.01],'Lower',[0.0,0.0],'Upper',[1,1])
p1 = bass_fit_1.p;
q1 = bass_fit_1.q;
p2 = bass_fit_2.p;
q2 = bass_fit_2.q;
p3 = bass_fit_3.p;
q3 = bass_fit_3.q;
p4 = bass_fit_4.p;
q4 = bass_fit_4.q;
x1 = r1;
x2 = r2;
x3 = r3;
x4 = 13*12+1:324;
%x4 = r4;
y1 = (1-exp(-x1.*(p1+q1))) ./ (1+(q1/p1)*exp(-x1.*(p1+q1)));
y2 = (1-exp(-x2.*(p2+q2))) ./ (1+(q2/p2)*exp(-x2.*(p2+q2)));
y3 = (1-exp(-x3.*(p3+q3))) ./ (1+(q3/p3)*exp(-x3.*(p3+q3)));
y4 = (1-exp(-x4.*(p4+q4))) ./ (1+(q4/p4)*exp(-x4.*(p4+q4)));

clf(figure(2))
hold on
plot(x1, y1*S1, 'k','linewidth',2)
plot(x2, y2*S2, 'b','linewidth',2)
plot(x3, y3*S3, 'g','linewidth',2)
plot(x4, y4*S4, 'r','linewidth',2)
hold off
hold on
plot([r1 r2 r3 r4], sum(raw_data(:,1:14*12),1), 'x')
hold off
legend('1999-2006','2007-2009','2010-2012','2012-','data')
legend('location','northwest')
xlabel('Year')
ylabel('Number of Adopters')
box on
grid on
%axis([1 193 0 40000])
axis([1 313 0 1400000])
set(findall(gcf,'type','text'),'fontsize',14)
set(gca,'fontsize',14)
set(gca,'XTick',13:60:313)
set(gca,'XTickLabel',{'2000','2005','2010','2015','2020','2025'})
%set(gca,'YTick',0:10000:40000)
%set(gca,'YTickLabel',{'0','10000','20000','30000','40000'})
set(gca,'YTick',0:200000:1400000)
set(gca,'YTickLabel',{'0',...
    '200000',...
    '400000',...
    '600000',...
    '800000',...
    '1000000',...
    '1200000',...
    '1400000'})
