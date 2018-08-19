import {
  Component,
  OnInit,
  Inject,
  Input,
  SimpleChange,
  EventEmitter,
  Output
} from "@angular/core";
import {
  MatSnackBar,
  MatSnackBarRef,
  MAT_SNACK_BAR_DATA
} from "@angular/material";
import {
  FormControl,
  FormGroup,
  FormBuilder,
  ValidatorFn,
  AbstractControl
} from "@angular/forms";
import { OrderPricing, OrderItem } from "../../db/order.model";
import { OrderService } from "../../db/order.service";
import { InventoryService } from "../../db/inventory.service";
import { Observable, of } from "rxjs";
import { Stock } from "../../db/inventory.model";
import { DocumentType } from "../../db/document.model";
import {
  debounceTime,
  distinctUntilChanged,
  switchMap,
  startWith,
  map,
  filter
} from "rxjs/operators";
import { OrderStockInfoComponent } from "../order-stock-info/order-stock-info.component";
import { OrderPricingInfoComponent } from "../order-pricing-info/order-pricing-info.component";
import { OfferService } from "../../db/offer.service";
import { Offer, OfferType } from "../../db/offer.model";

@Component({
  selector: "app-order-item",
  templateUrl: "./order-item.component.html",
  styleUrls: ["./order-item.component.css"]
})
export class OrderItemComponent implements OnInit {
  @Input()
  contactId: string;
  @Input()
  docType: DocumentType;
  @Input()
  form: FormGroup;
  @Input()
  index: number;
  @Output()
  offerSelected = new EventEmitter<number>();
  @Output()
  itemDeleted = new EventEmitter<number>();

  offerPicker: FormControl;

  // standalone
  total: number;
  snackbarRef: any;

  // autocomplete observables
  offers$: Observable<Offer[]>;
  pricing$: Observable<OrderPricing>;
  stocks$: Observable<Stock[]>;

  constructor(
    private formBuilder: FormBuilder,
    private snackbar: MatSnackBar,
    private offerService: OfferService,
    private orderService: OrderService,
    private inventoryService: InventoryService
  ) {
    this.offerPicker = new FormControl();
  }

  ngOnInit() {}

  ngOnChanges(changes: SimpleChange) {
    // this.form.patchValue(this.item);
    const offer = this.form.get("offer").value;
    if (offer !== null) this.offerPicker.setValue(offer);
    this.form.get("quantity").valueChanges.subscribe(() => this.updateTotal());
    this.form.get("price").valueChanges.subscribe(() => this.updateTotal());
    this.updateTotal();
  }

  selectOffer(offer) {
    if (offer === null) {
      return;
    }

    if (this.form.get("offer").value === null) {
      this.offerSelected.emit(this.index);
    }

    this.form.get("offer").setValue(offer);
    this.pricing$ = this.orderService.getPricing(
      offer.id,
      this.contactId,
      this.docType
    );
    this.stocks$ =
      offer.type === OfferType.PRODUCT
        ? this.inventoryService.getStock(offer.id)
        : of([]);
  }

  showCustomize(): boolean {
    return this.form.get("custom_description").value !== null;
  }

  toggleCustomize() {
    const custom = this.form.get("custom_description");
    custom.setValue(custom.value === null ? "" : null);
  }

  showSnackBar(type) {
    if (this.snackbarRef) {
      this.hideSnackBar();
    }

    const snackbars = {
      stocks: {
        component: OrderStockInfoComponent,
        data: this.stocks$
      },
      pricing: {
        component: OrderPricingInfoComponent,
        data: this.pricing$
      }
    };

    this.snackbarRef = this.snackbar.openFromComponent(
      snackbars[type].component,
      {
        data: snackbars[type].data
      }
    );
  }

  hideSnackBar() {
    this.snackbarRef.dismiss();
    this.snackbarRef = null;
  }

  updateTotal() {
    this.total = this.form.get("quantity").value * this.form.get("price").value;
  }

  deleteItem() {
    this.itemDeleted.emit(this.index);
  }

  // offerValidator(): ValidatorFn {
  //     return (control: AbstractControl): { [key: string]: any } => {
  //         if (control.value instanceof Offer)
  //         return forbidden ? { 'forbiddenName': { value: control.value } } : null;
  //     };
  // }
}
