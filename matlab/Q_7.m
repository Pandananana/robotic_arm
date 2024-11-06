function [Fk] = Q_7(t0, t1, q0, q0dd, q1, q1dd, nums, T4_0, J4, v0, v1,a0,a1)
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
    
    T_pol = [1, t0, t0^2, t0^3, t0^4, t0^5;
              0, 1, 2*t0, 3*t0^2, 4*t0^3, 5*t0^4;
              0, 0, 2, 6*t0, 12*t0^2, 20*t0^3;
              1, t1, t1^2, t1^3, t1^4, t1^5;
              0, 1, 2*t1, 3*t1^2, 4*t1^3, 5*t1^4;
              0, 0, 2, 6*t1, 12*t1^2, 20*t1^3];
    
    for i = 1:length(q0);   

        rhs(:,i) = [q0(i), q0d(i), q0dd(i), q1(i), q1d(i), q1dd(i)];
        C_0(i,:) = T_pol \ rhs(:,i);

    end
    t = linspace(t0,t1,nums);
    q_1 = C_0(1,1)+C_0(1,2)*t+C_0(1,3)*t.^2+C_0(1,4)*t.^3+C_0(1,5)*t.^4+C_0(1,6)*t.^5;
    q_2 = C_0(2,1)+C_0(2,2)*t+C_0(2,3)*t.^2+C_0(2,4)*t.^3+C_0(2,5)*t.^4+C_0(2,6)*t.^5;
    q_3 = C_0(3,1)+C_0(3,2)*t+C_0(3,3)*t.^2+C_0(3,4)*t.^3+C_0(3,5)*t.^4+C_0(3,6)*t.^5;
    q_4 = C_0(4,1)+C_0(4,2)*t+C_0(4,3)*t.^2+C_0(4,4)*t.^3+C_0(4,5)*t.^4+C_0(4,6)*t.^5;
    for i=1:nums
        FK_0 = T4_0_f(q_1(i),q_2(i),q_3(i),q_4(i));
        Fk(:,i) = FK_0(1:3,4);
    end
end