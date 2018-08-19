import { Component, OnInit } from "@angular/core";
import { DiscountFormComponent } from "../discount-form/discount-form.component";
import { MatDialog } from "@angular/material";
import { PaymentAllocationPickerComponent } from "../payment-allocation-picker/payment-allocation-picker.component";

@Component({
  selector: "app-payment-allocation",
  templateUrl: "./payment-allocation.component.html",
  styleUrls: ["./payment-allocation.component.css"]
})
export class PaymentAllocationComponent implements OnInit {
  constructor(private dialog: MatDialog) {}

  ngOnInit() {}

  openDiscountDialog() {
    const dialogRef = this.dialog.open(DiscountFormComponent, {
      width: "800px",
      // height: "768px",
      disableClose: true
    });

    dialogRef.afterClosed().subscribe(result => {
      console.log(`Dialog result: ${result}`);
    });
  }

  openAllocationDialog() {
    const dialogRef = this.dialog.open(PaymentAllocationPickerComponent, {
      width: "800px",
      // height: "768px",
      disableClose: true
    });

    dialogRef.afterClosed().subscribe(result => {
      console.log(`Dialog result: ${result}`);
    });
  }
}
