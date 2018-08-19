import { Component, OnInit, Inject } from "@angular/core";
import { MAT_SNACK_BAR_DATA } from "@angular/material";
import { Observable } from "rxjs";
import { Stock } from "../../db/inventory.model";

@Component({
  selector: "app-order-stock-info",
  templateUrl: "./order-stock-info.component.html",
  styleUrls: ["./order-stock-info.component.css"]
})
export class OrderStockInfoComponent implements OnInit {
  constructor(
    @Inject(MAT_SNACK_BAR_DATA) public stocks$: Observable<Stock[]>
  ) {}

  ngOnInit() {}
}
