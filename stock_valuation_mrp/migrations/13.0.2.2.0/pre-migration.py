# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE
            stock_valuation_layer
        SET
            origin_type=case
                when sm.raw_material_production_id is not null or sm.production_id is not null then 'mrp'
                when sm.unbuild_id is not null then 'unbuild'
                else ''
            end
        FROM
            stock_valuation_layer svl
        INNER JOIN
            stock_move sm on sm.id=svl.stock_move_id
        WHERE
            stock_valuation_layer.id = svl.id
            and coalesce(stock_valuation_layer.origin_type, '') = ''
        """,
    )
