import { Component, OnInit } from "@angular/core";
import { FormGroup, FormBuilder, FormArray } from "@angular/forms";

@Component({
  selector: "app-location-adjustment-form",
  templateUrl: "./location-adjustment-form.component.html",
  styleUrls: ["./location-adjustment-form.component.css"]
})
export class LocationAdjustmentFormComponent implements OnInit {
  form: FormGroup;
  items: FormArray;

  constructor(private formBuilder: FormBuilder) {}

  ngOnInit() {
    this.form = this.formBuilder.group({
      origin: null,
      destination: null,
      ref_no: null,
      date: null
    });

    const locationItem = this.formBuilder.group({
      offer_id: null,
      quantity: null
    });

    this.items = this.formBuilder.array([locationItem]);

    this.form.setControl("items", this.items);
  }
}
