from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    location_ids = env['stock.location'].search([('usage', '=', 'production')])
    if len(location_ids) > 1:
        locations = str(tuple(location_ids.ids))
        condition = f"location_dest_id in {locations}"
    else:
        location = location_ids.id
        condition = f"location_dest_id = {location}"
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE mrp_production
        SET location_dest_id = location_src_id
        WHERE {condition};
        """,
    )
