
function [J] = Jacobi_Revolute(o, z, joint_index)
   
    num_o = size(o,2);
    num_z = size(z,2);
    for i=1:num_z
        Jv(:,i) = cross(z(:,i),o(:,joint_index)-o(:,i));
        Jw(:,i) = z(:,i);
    end
    J = [Jv;Jw]
end