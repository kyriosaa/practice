% Purit Hongjirakul 黃子奇 114998411
% Homework question 2

figure(1);
grid on;
hold on;

x = [1, 2, 3];
y = [0.491666 0.111262 2.61608 0.101136 0.001488 0.062088 0 0.101136;
     1.355137 0.685360 2.61608 0.101136 0.003466 0.382618 0 0.101136;
     2.794254 2.736705 2.61608 0.101136 0.006762 1.526368 0 0.101136];

bar(x, y, 'stacked');
xticks(x);
xticklabels({'300', '750', '1500'});
xlim([0 4.5]);
ylim([0 10]);

title('HW 2');
xlabel('Po (W)');
ylabel('Loss (W)');
legend('Psw (main)', 'Pcond (main)', 'Pcoss (main)', 'Pdriving (main)',...
       'Psw (sub)', 'Pcond (sub)', 'Pcoss (sub)', 'Pdriving (sub)');