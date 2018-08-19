import { Component, OnInit, Input, EventEmitter, Output } from "@angular/core";
import { FormGroup, FormBuilder } from "@angular/forms";
import { Contact, EMPTY_CONTACT } from "../../db/contact.model";
import { clone } from "../../app-common/util";

@Component({
  selector: "app-contact-form",
  templateUrl: "./contact-form.component.html",
  styleUrls: ["./contact-form.component.css"]
})
export class ContactFormComponent implements OnInit {
  @Input()
  contact: Contact;
  @Output()
  contactSaved = new EventEmitter<Contact>();

  form: FormGroup;

  constructor(private formBuilder: FormBuilder) {}

  ngOnInit() {
    this.contact = this.contact ? this.contact : clone(EMPTY_CONTACT);
    this.form = this.formBuilder.group(this.contact);
    this.form.setControl(
      "numbers",
      this.formBuilder.array(
        this.contact.numbers.map(num => this.formBuilder.control(num))
      )
    );
    this.form.setControl(
      "addresses",
      this.formBuilder.array(
        this.contact.addresses.map(num => this.formBuilder.control(num))
      )
    );
    this.form.setControl(
      "emails",
      this.formBuilder.array(
        this.contact.emails.map(num => this.formBuilder.control(num))
      )
    );
    this.form.setControl(
      "links",
      this.formBuilder.array(
        this.contact.links.map(num => this.formBuilder.control(num))
      )
    );
  }

  onSave() {
    this.contactSaved.emit(this.form.value);
    console.log(this.form.value);
  }
}
