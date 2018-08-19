import { Component, OnInit, Inject } from "@angular/core";
import { MAT_SNACK_BAR_DATA } from "@angular/material";
import { Observable } from "rxjs";
import { OrderPricing } from "../../db/order.model";

@Component({
  selector: "app-order-pricing-info",
  templateUrl: "./order-pricing-info.component.html",
  styleUrls: ["./order-pricing-info.component.css"]
})
export class OrderPricingInfoComponent implements OnInit {
  constructor(
    @Inject(MAT_SNACK_BAR_DATA) public pricing$: Observable<OrderPricing>
  ) {}

  ngOnInit() {}
}
