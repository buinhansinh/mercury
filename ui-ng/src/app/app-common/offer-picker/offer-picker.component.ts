import {
  Component,
  OnInit,
  Output,
  EventEmitter,
  Input,
  SimpleChange
} from "@angular/core";
import { Observable, of } from "rxjs";
import { Offer } from "../../db/offer.model";
import { FormControl } from "@angular/forms";
import {
  debounceTime,
  distinctUntilChanged,
  switchMap,
  startWith
} from "rxjs/operators";
import { OfferService } from "../../db/offer.service";

@Component({
  selector: "app-offer-picker",
  templateUrl: "./offer-picker.component.html",
  styleUrls: ["./offer-picker.component.css"]
})
export class OfferPickerComponent implements OnInit {
  @Input()
  form: FormControl;
  @Input()
  offer: Offer;
  @Input()
  placeholder: string;
  @Output()
  offerPicked = new EventEmitter<Offer>();

  offers$: Observable<Offer[]>;

  constructor(private offerService: OfferService) {}

  ngOnInit() {
    this.offers$ = this.form.valueChanges.pipe(
      debounceTime(300), // wait 300ms after each keystroke before considering the term
      distinctUntilChanged(), // ignore new term if same as previous term
      switchMap((terms: string | Offer) => this.onSearch(terms)) // switch to new search observable each time the term changes
    );
  }

  ngOnChanges(changes: SimpleChange) {
    this.onSelect();
  }

  onSearch(terms: string | Offer): Observable<Offer[]> {
    return typeof terms === "string"
      ? this.offerService.search(<string>terms)
      : of([]);
  }

  onSelect() {
    this.offer = this.form.value;
    this.offerPicked.emit(this.form.value); // we're getting a offer from autocomplete
  }

  reset() {
    this.form.setValue(this.offer);
  }

  offerDisplay(offer) {
    return offer ? offer.description : null;
  }
}
