<%!
    import spline.format as libfmt
%>

## TODO wild idea: change the escape filter to allow automatically rendering
## certain types in custom ways?
<%def name="timestamp(dt)">
${dt.strftime("%a %b %d, %Y @ %H:%M")}
</%def>

<%def name="relative_timestamp(dt)"><time datetime="${dt.isoformat()}">${libfmt.format_relative_date(dt)}</time></%def>

<%def name="user(user)">
% if user:
${user.name}
% else:
## pastes only, TODO
Someone
% endif
</%def>
