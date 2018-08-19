import { Component, OnInit } from "@angular/core";
import { FormGroup, FormBuilder } from "@angular/forms";
import {
  OrderTransfer,
  EMPTY_ORDER_TRANSFER
} from "../../db/order-transfer.model";
import { clone } from "../../app-common/util";
import { EMPTY_PRODUCT } from "../../db/offer.model";

@Component({
  selector: "app-order-transfer-form",
  templateUrl: "./order-transfer-form.component.html",
  styleUrls: ["./order-transfer-form.component.css"]
})
export class OrderTransferFormComponent implements OnInit {
  form: FormGroup;
  model: OrderTransfer;

  constructor(private formBuilder: FormBuilder) {}

  ngOnInit() {
    this.model = this.model ? this.model : clone(EMPTY_ORDER_TRANSFER);
    this.model.quantities = [1, 2];
    console.log(this.model);
    this.form = this.formBuilder.group({
      id: null,
      date: null,
      ref_no: null,
      status: null
    });
    const quantities = this.formBuilder.array(
      this.model.quantities.map(q =>
        this.formBuilder.control({ quantities: q })
      )
    );
    this.form.setControl("quantities", quantities);
  }
}
