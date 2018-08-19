import { Component, OnInit, Input, Output, EventEmitter } from "@angular/core";
import { Offer, EMPTY_PRODUCT, EMPTY_SERVICE } from "../../db/offer.model";
import { FormBuilder, FormGroup } from "@angular/forms";
import { clone } from "../../app-common/util";

@Component({
  selector: "app-service-form",
  templateUrl: "./service-form.component.html",
  styleUrls: ["./service-form.component.css"]
})
export class ServiceFormComponent implements OnInit {
  @Input()
  offer: Offer;
  @Output()
  offerSaved = new EventEmitter<Offer>();

  form: FormGroup;

  constructor(private formBuilder: FormBuilder) {}

  ngOnInit() {
    this.offer = this.offer ? this.offer : clone(EMPTY_SERVICE);
    this.form = this.formBuilder.group(this.offer);
    const props = this.formBuilder.array(
      Object.entries(this.offer.properties).map(([name, value]) =>
        this.formBuilder.group({ name: name, value: value })
      )
    );
    console.log(props);
    this.form.setControl("properties", props);
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
}
