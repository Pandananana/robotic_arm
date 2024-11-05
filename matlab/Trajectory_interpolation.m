


function [Coefficients] = Trajectory_interpolation(t0, t1, q0, q0d, q0dd, q1, q1d, q1dd)
    
    
    T_pol = [1, t0, t0^2, t0^3, t0^4, t0^5;
              0, 1, 2*t0, 3*t0^2, 4*t0^3, 5*t0^4;
              0, 0, 2, 6*t0, 12*t0^2, 20*t0^3;
              1, t1, t1^2, t1^3, t1^4, t1^5;
              0, 1, 2*t1, 3*t1^2, 4*t1^3, 5*t1^4;
              0, 0, 2, 6*t1, 12*t1^2, 20*t1^3];
    
    for i = 1:length(q0);   

        rhs(:,i) = [q0(i), q0d(i), q0dd(i), q1(i), q1d(i), q1dd(i)];
        Coefficients(i,:) = T_pol \ rhs(:,i);

    end
    
end