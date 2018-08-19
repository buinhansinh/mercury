import { Component, OnInit } from "@angular/core";
import { ORDERS } from "../../db/order.mock";
import { Order } from "../../db/order.model";

@Component({
  selector: "app-sales-order",
  templateUrl: "./sales-order.component.html",
  styleUrls: ["./sales-order.component.css"]
})
export class SalesOrderComponent implements OnInit {
  order: Order;

  constructor() {
    this.order = ORDERS[0];
  }

  ngOnInit() {}
}
