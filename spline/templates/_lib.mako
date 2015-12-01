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

## TODO much of this should be the responsibility of a little html library
<%def name="form(action, method='POST', class_='', rel='', upload=False)">
<form action="${action}" method="${method}" class="${class_}" rel="${rel}"
% if upload:
enctype="multipart/form-data"
% endif
>
% if method != 'GET':
<input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
% endif
${caller.body()}
</form>
</%def>
