% Single-Stage Filter with Same Ripple

part_a;

% from part a, we already calculated H_target
H_target = H_mag; 

% for single-stage filter at switching frequency
% H(jω) = 1 / (1 + jω/(Q*ω_o) - ω²/ω_o²)

Q1_new = 1;
omega_sw = 2*pi*50e3;

% |H(jω_sw)| = H_target
% substitute s = jω_sw
% |H| = 1 / |1 + jω_sw/(ω_o) - ω_sw²/ω_o²|
% |H| = 1 / √[(1 - ω_sw²/ω_o²)² + (ω_sw/ω_o)²]

% find the right ω_o
omega_o_test = logspace(3, 6, 10000); 

H_single_test = zeros(size(omega_o_test));
for i = 1:length(omega_o_test)
    omega_o = omega_o_test(i);
    
    real_part = 1 - omega_sw^2/omega_o^2;
    imag_part = omega_sw/(Q1_new*omega_o);
    
    H_single_test(i) = 1 / sqrt(real_part^2 + imag_part^2);
end

% find the ω_o that gives us H_target
[~, idx] = min(abs(H_single_test - H_target));
omega_o_new = omega_o_test(idx);

fprintf('Required ω_o1 = %.2f rad/s\n', omega_o_new);

% calc L1 and C1
L1_new = 1/omega_o_new;  
C1_new = 1/omega_o_new;  

fprintf('L1 = %.2f μH\n', L1_new*1e6);
fprintf('C1 = %.2f μF\n', C1_new*1e6);