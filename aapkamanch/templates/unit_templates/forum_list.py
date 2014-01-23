# Copyright Aap Ka Manch
# License GNU General Public Licence

from __future__ import unicode_literals

import webnotes
from webnotes.utils import now_datetime, get_datetime_str
from aapkamanch.helpers import get_access, get_views

def get_unit_html(context):
	context["post_list_html"] = get_post_list_html(context.get("name"), context.get("view"))
	
@webnotes.whitelist(allow_guest=True)
def get_post_list_html(unit, view, limit_start=0, limit_length=20):
	access = get_access(unit)
	if webnotes.local.form_dict.cmd=="get_post_list_html":
		# for paging
		if not access.get("read"):
			raise webnotes.PermissionError
			
	if view=="feed":
		order_by = "p.creation desc"
	else:
		now = get_datetime_str(now_datetime())
		order_by = "(p.upvotes + post_reply_count - (timestampdiff(hour, p.creation, \"{}\") / 2)) desc, p.creation desc".format(now)
	
	posts = webnotes.conn.sql("""select p.*, pr.user_image, pr.first_name, pr.last_name,
		(select count(pc.name) from `tabPost` pc where pc.parent_post=p.name) as post_reply_count
		from tabPost p, tabProfile pr
		where p.unit=%s and pr.name = p.owner and ifnull(p.parent_post, '')=''
		order by {order_by} limit %s, %s""".format(order_by=order_by), 
			(unit, int(limit_start), int(limit_length)), as_dict=True)
			
	return webnotes.get_template("templates/includes/post_list.html").render({
		"posts": posts, 
		"limit_start": limit_start,
		"view": view,
		"view_options": get_views(unit).get(view)
	})