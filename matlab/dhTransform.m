function T = dhTransform(theta, d, a, alpha)
    % dhTransform - Create homogeneous transformation matrix from DH parameters
    % 
    % Inputs:
    %   theta - Joint angle (symbolic or real, real values in degrees)
    %   d     - Link offset
    %   a     - Link length
    %   alpha - Link twist angle (symbolic or real, real values in degrees)
    %
    % Output:
    %   T - 4x4 homogeneous transformation matrix
    
    % If input is symbolic, use sin/cos, otherwise use sind/cosd
    if isa(theta, 'sym')
        ct = cos(theta);
        st = sin(theta);
    else
        ct = cosd(theta);
        st = sind(theta);
    end
    
    if isa(alpha, 'sym')
        ca = cos(alpha);
        sa = sin(alpha);
    else
        ca = cosd(alpha);
        sa = sind(alpha);
    end
    
    % Create transformation matrix
    T = [ct, -st*ca,  st*sa, a*ct;
         st,  ct*ca, -ct*sa, a*st;
          0,    sa,     ca,    d;
          0,     0,      0,    1];
end