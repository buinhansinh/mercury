import { Component, OnInit, Input, Output, EventEmitter } from "@angular/core";
import { Offer, EMPTY_PRODUCT } from "../../db/offer.model";
import { FormBuilder, FormGroup, FormArray, Validators } from "@angular/forms";
import { clone, capitalize } from "../../app-common/util";

@Component({
  selector: "app-product-form",
  templateUrl: "./product-form.component.html",
  styleUrls: ["./product-form.component.css"]
})
export class ProductFormComponent implements OnInit {
  @Input()
  offer: Offer;
  @Output()
  offerSaved = new EventEmitter<Offer>();

  form: FormGroup;
  properties: FormArray;

  constructor(private formBuilder: FormBuilder) {}

  ngOnInit() {
    this.buildForm();
  }

  ngOnChange() {
    this.buildForm();
  }

  buildForm() {
    // ensure there is an offer
    this.offer = this.offer ? this.offer : clone(EMPTY_PRODUCT);

    this.form = this.formBuilder.group(this.offer);
    this.properties = this.formBuilder.array(
      Object.entries(this.offer.properties).map(([name, value]) => {
        const required = name === "brand" || name === "model";
        return this.formBuilder.group({
          name: [capitalize(name), Validators.required],
          value: [value, Validators.required],
          required: required
        });
      })
    );
    this.form.setControl("properties", this.properties);
  }

  addProperty() {
    const prop: FormGroup = this.formBuilder.group({
      name: "",
      value: "",
      required: false
    });
    this.properties.push(prop);
  }

  removeProperty(i: number) {
    this.properties.removeAt(i);
  }

  onSave() {
    const props = {};
    this.form.value.properties.map(p => (props[p.name] = p.value));
    this.offer = {
      id: this.form.value.id,
      type: this.offer.type,
      properties: props,
      description: Object.values(props).join(" ")
    };

    this.offerSaved.emit(this.offer);
    console.log(this.offer);
  }

  onSubmit() {
    this.onSave();
  }
}
