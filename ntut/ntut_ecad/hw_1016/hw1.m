% Purit Hongjirakul 黃子奇 114998411
% Homework question 1

figure(1);
grid on;
hold on;

x = linspace(10, 100, 10);
y_tradA     = [91.16, 95.29, 96.24, 96.67, 96.84,...
               96.80, 96.69, 96.55, 96.36, 96.15];
y_tradB     = [90.14, 94.01, 95.18, 95.78, 95.98,...
               96.09, 96.07, 96.06, 95.89, 95.68];
y_proposed  = [87.78, 93.45, 94.90, 95.54, 95.87,...
               96.01, 96.07, 96.02, 95.90, 95.70];

plot(x, y_tradA, 'b-');
plot(x, y_tradB, 'y-');
plot(x, y_proposed, 'r-');
xlim([0 100]);
ylim([85 100]);
yticks(86:2:100);

title('HW 1');
xlabel('Load 750 W (%)');
ylabel('Efficiency (%)');
legend('Traditional LLC A', 'Traditional LLC B', 'Proposed LLC');