function [q1,q2,q3,q4] = Config4DOF(o4,x4_z,d1,a2,a3,a4)
    q1 = atan2(o4(2),o4(1));

    x4_0 = [sqrt(1-x4_z^2)*cos(q1);
            sqrt(1-x4_z^2)*sin(q1);
            x4_z];

    oc = o4 - a4 * x4_0;

    s = oc(3) - d1;
    r=sqrt(oc(1)^2+oc(2)^2);
    c3 = (r^2 + s^2 - a2^2-a3^2)/(2*a2*a3);

    q3 = atan2(-sqrt(1-c3^2), c3);
    q2 = atan2(s,r) - atan2(a3*sin(q3),a2+a3*c3);
    q4 = asin(x4_z) - (q2 + q3);
end