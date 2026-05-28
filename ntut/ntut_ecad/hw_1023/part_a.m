%  Predict Output Voltage Ripple with Two-Stage Filter

L1  = 318.5e-6; % H
L2  = 31.85e-6; % H
C1  = 318.5e-6; % F
C2  = 31.85e-6; % F
R   = 1;        % Ohm
Vin = 6;        % V
D   = 10/20;    % Duty cycle = 0.5

% switching freq
f_sw        = 50e3;  % Hz
omega_sw    = 2*pi*f_sw;   

% resonant freq & Q factors
omega_o1 = 1/sqrt(L1*C1);
Q1 = R*sqrt(C1/L1);
omega_o2 = 1/sqrt(L2*C2);
Q2 = R*sqrt(C2/L2);

fprintf('ω_o1 = %.2f rad/s (f_o1 = %.2f Hz)\n', omega_o1, omega_o1/(2*pi));
fprintf('Q1 = %.2f\n', Q1);
fprintf('ω_o2 = %.2f rad/s (f_o2 = %.2f Hz)\n', omega_o2, omega_o2/(2*pi));
fprintf('Q2 = %.2f\n\n', Q2);

% transfer func at switching freq
s = 1j*omega_sw;

H_num   = 1;
H_den1  = (1 + s/(Q1*omega_o1) + (s^2)/(omega_o1^2));
H_den2  = (1 + s/(Q2*omega_o2) + (s^2)/(omega_o2^2));

H = H_num / (H_den1 * H_den2);
H_mag = abs(H);
H_dB = 20*log10(H_mag);

fprintf('Transfer function magnitude at f_sw:\n');
fprintf('|H(jω)| = %.6f = %.2f dB\n\n', H_mag, H_dB);

% first harmonic amplitude of square wave
% for 50% duty cycle: v1 = (4*Vin/pi) * sin(pi*D)
v1_input = (4*Vin/pi) * sin(pi*D);

fprintf('First harmonic input amplitude: %.3f V\n', v1_input);

% output voltage ripple
v1_output = v1_input * H_mag;

fprintf('Output voltage ripple (first harmonic): %.3f mV peak\n', v1_output*1000);
fprintf('Output voltage ripple (peak-to-peak): %.3f mV\n\n', 2*v1_output*1000);