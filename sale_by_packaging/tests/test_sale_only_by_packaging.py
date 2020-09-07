# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.exceptions import ValidationError
from odoo.tests import SavepointCase, Form


class TestSaleProductByPackagingOnly(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.product = cls.env.ref("product.product_product_9")
        cls.packaging_5 = cls.env["product.packaging"].create(
            {"name": "Test packaging 5", "product_id": cls.product.id, "qty": 5.0}
        )
        cls.order = cls.env["sale.order"].create({"partner_id": cls.partner.id})
        cls.packaging_15 = cls.env["product.packaging"].create(
            {"name": "Test packaging 15", "product_id": cls.product.id, "qty": 15.0}
        )
        cls.packaging_30 = cls.env["product.packaging"].create(
            {"name": "Test packaging 30", "product_id": cls.product.id, "qty": 30.0}
        )

    # def test_onchange_qty_is_pack_multiple(self):
    #     # sale_form = Form(self.order)
    #     # with sale_form.order_line.new() as line_form:
    #     #     line_form.product_id = self.product
    #     #     line_form.product_uom_qty = 2
    #     #     line_form.product_uom = self.product.uom_id
    #     # sale_form.save()
    #     order_line = self.env["sale.order.line"].create(
    #         {
    #             "order_id": self.order.id,
    #             "product_id": self.product.id,
    #             "product_uom": self.product.uom_id.id,
    #             "product_uom_qty": 5.0,
    #         }
    #     )
    #     res = order_line._onchange_product_uom_qty()
    #     self.assertFalse(res)

    #     self.product.write({"sell_only_by_packaging": True})
    #     res = order_line._onchange_product_uom_qty()
    #     self.assertTrue(res)

    #     order_line.product_id_change()
    #     res = order_line._onchange_product_uom_qty()
    #     self.assertFalse(res)

    #     order_line.write({"product_uom_qty": 3.0})
    #     res = order_line._onchange_product_uom_qty()
    #     self.assertTrue(res)

    #     order_line.write({"product_uom_qty": self.packaging_5.qty * 2})
    #     res = order_line._onchange_product_uom_qty()
    #     self.assertFalse(res)

    def test_write_auto_fill_packaging(self):
        sale_form = Form(self.order)
        with sale_form.order_line.new() as line_form:
            line_form.product_id = self.product
            line_form.product_uom = self.product.uom_id
        sale_form.save()
        order_line = self.order.order_line[0]
        import pdb; pdb.set_trace()
        # order_line = self.env["sale.order.linne"].create(
        #     {
        #         "order_id": self.order.id,
        #         "product_id": self.product.id,
        #         "product_uom": self.product.uom_id.id,
        #     }
        # )
        self.assertFalse(order_line.product_packaging)
        self.assertFalse(order_line.product_packaging_qty)

        order_line.write({"product_uom_qty": 5.0})
        self.assertFalse(order_line.product_packaging)
        self.assertFalse(order_line.product_packaging_qty)

        self.product.write({"sell_only_by_packaging": True})
        self.assertFalse(order_line.product_packaging)
        self.assertFalse(order_line.product_packaging_qty)

        order_line.with_context(foo=1).write({"product_uom_qty": self.packaging_5.qty * 2})
        self.assertTrue(order_line.product_packaging)
        self.assertTrue(order_line.product_packaging_qty)
        self.assertEqual(order_line.product_packaging, self.packaging_5)
        self.assertEqual(order_line.product_packaging_qty, 2)

        
        # if the qty changes, the product packaging stays the same
        order_line.write({"product_uom_qty": self.packaging_15.qty * 2})
        self.assertEqual(order_line.product_packaging, self.packaging_5)

        with self.assertRaises(ValidationError):
            order_line.write({"product_packaging": False})

    def test_create_auto_fill_packaging(self):
        # sell_only_by_packaging is default False
        order_line_1 = self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": self.packaging_5.qty * 2,
            }
        )
        self.assertFalse(order_line_1.product_packaging)
        self.assertFalse(order_line_1.product_packaging_qty)

        self.product.write({"sell_only_by_packaging": True})
        order_line_1 = self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": self.packaging_5.qty * 2,
            }
        )
        self.assertTrue(order_line_1.product_packaging)
        self.assertTrue(order_line_1.product_packaging_qty)
        self.assertEqual(order_line_1.product_packaging, self.packaging_5)
        self.assertEqual(order_line_1.product_packaging_qty, 2)

        with self.assertRaises(ValidationError):
            self.env["sale.order.line"].create(
                {
                    "order_id": self.order.id,
                    "product_id": self.product.id,
                    "product_uom": self.product.uom_id.id,
                    "product_uom_qty": 2,
                }
            )
