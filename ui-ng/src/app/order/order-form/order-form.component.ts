import { Component, OnInit, Input } from "@angular/core";
import { OrderItem, Order } from "../../db/order.model";
import { range } from "../../app-common/util";
import { OfferType } from "../../db/offer.model";
import { Contact } from "../../db/contact.model";
import { FormControl, FormBuilder, FormGroup, FormArray } from "@angular/forms";
import { ORDERS } from "../../db/order.mock";

@Component({
  selector: "app-order-form",
  templateUrl: "./order-form.component.html",
  styleUrls: ["./order-form.component.css"]
})
export class OrderFormComponent implements OnInit {
  @Input()
  order: Order;

  form: FormGroup;
  item_array: FormArray;
  contactPicker: FormControl;
  EMPTY_ORDERITEM: OrderItem = {
    offer: null,
    custom_description: null,
    quantity: 0,
    price: 0
  };

  constructor(private formBuilder: FormBuilder) {
    this.contactPicker = new FormControl();
  }

  ngOnInit() {
    // test code
    this.form = this.formBuilder.group(this.order);

    // long-winded way of creating a form array
    const item_groups: FormGroup[] = this.order.items.map(item =>
      this.formBuilder.group(item)
    );

    this.item_array = this.formBuilder.array(item_groups);
    this.form.setControl("items", this.item_array);

    // add an empty item at the start
    this.appendEmptyItem();

    this.contactPicker.setValue(this.order.contact);
  }

  createOrderItem() {
    return {
      offer: null,
      custom_description: null,
      quantity: 0,
      price: 0
    };
  }

  appendEmptyItem() {
    const new_item: FormGroup = this.formBuilder.group(this.createOrderItem());
    this.item_array.push(new_item);
  }

  onOfferSelected(index: number) {
    console.log("onOfferSelected", index);
    if (index === this.item_array.length - 1) {
      this.appendEmptyItem();
    }
  }

  onItemDelete(index: number) {
    if (
      index === this.item_array.length - 1 &&
      this.item_array.at(index).get("offer").value === null
    ) {
    } else {
      this.item_array.removeAt(index);
    }
  }

  onSave() {
    console.log(this.form.value);
  }
}
