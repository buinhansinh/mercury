import {
  Component,
  OnInit,
  Output,
  EventEmitter,
  Input,
  SimpleChange
} from "@angular/core";
import { Observable, of } from "rxjs";
import { FormControl } from "@angular/forms";
import {
  debounceTime,
  distinctUntilChanged,
  switchMap,
  startWith
} from "rxjs/operators";
import { Contact } from "../../db/contact.model";
import { ContactService } from "../../db/contact.service";

@Component({
  selector: "app-contact-picker",
  templateUrl: "./contact-picker.component.html",
  styleUrls: ["./contact-picker.component.css"]
})
export class ContactPickerComponent implements OnInit {
  @Input()
  label: string;
  @Input()
  placeholder: string;
  @Input()
  form: FormControl;
  @Input()
  contact: Contact;
  @Output()
  contactPicked = new EventEmitter<Contact>();

  contacts$: Observable<Contact[]>;

  constructor(private contactService: ContactService) {}

  ngOnInit() {
    this.contacts$ = this.form.valueChanges.pipe(
      debounceTime(300), // wait 300ms after each keystroke before considering the term
      distinctUntilChanged(), // ignore new term if same as previous term
      switchMap((terms: string | Contact) => this.onSearch(terms)) // switch to new search observable each time the term changes
    );
  }

  ngOnChanges(changes: SimpleChange) {
    this.onSelect();
  }

  onSearch(terms: string | Contact): Observable<Contact[]> {
    return typeof terms === "string"
      ? this.contactService.search(<string>terms)
      : of([]);
  }

  onSelect() {
    this.contact = this.form.value;
    this.contactPicked.emit(this.form.value); // we're getting a contact from autocomplete
  }

  reset() {
    this.form.setValue(this.contact);
  }

  contactDisplay(contact) {
    return contact ? contact.name : null;
  }
}
