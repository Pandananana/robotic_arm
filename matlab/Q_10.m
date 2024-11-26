function [q0d,q1d] = Q_10(T, n, q0, q0dd, q1, q1dd, nums, T4_0, J4, v0, v1,a0,a1)
    t0 = 0;
    t1 = T/n;
    T4_0_f = matlabFunction(T4_0);
    J4_f = matlabFunction(J4);
    T_problem(:,:,1) = T4_0_f(q0(1),q0(2),q0(3),q0(4));
    T_problem(:,:,2) = T4_0_f(q1(1),q1(2),q1(3),q1(4));
    
    v = [0, -v0*sin(a0*pi/180), v0*cos(a0*pi/180), 0;
    0, -v1*sin(a1*pi/180), v1*cos(a1*pi/180) ,0];

    JJ(:,:,1) = J4_f(q0(1),q0(2),q0(3),q0(4));
	JJ(:,:,2) = J4_f(q1(1),q1(2),q1(3),q1(4));

    for i = 1:2

        Ryx = T_problem(2,1,i);
        Rxx = T_problem(1,1,i);
        Mask = [1,0,0,0,0,0;
                0,1,0,0,0,0;
                0,0,1,0,0,0;
                0,0,0,Ryx, -Rxx, 0];
        A4x6 = JJ(:,:,i);
        A4x4 = Mask*JJ(:,:,i);
        J_plus = ((transpose(A4x4)*A4x4)^-1)*transpose(A4x4);     % Underactuated arm (4 DOF < 6 DOF)
        q_dot7(:,i) = J_plus*v(i,:)';

    end
    q0d = q_dot7(:,1);
    q1d = q_dot7(:,2);
end