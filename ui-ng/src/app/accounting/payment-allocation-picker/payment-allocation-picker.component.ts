import { Component, OnInit, ViewChild } from "@angular/core";
import { MatPaginator, MatSort, MatTableDataSource } from "@angular/material";
import { SelectionModel } from "@angular/cdk/collections";

export interface Allocatable {
  id: string;
  ref_no: string;
  type: string;
  date: Date;
  amount: number;
}

const allocatables = [
  { id: "1", ref_no: "1", type: "invoice", date: new Date(), amount: 100 },
  {
    id: "1",
    ref_no: "in-3012",
    type: "invoice",
    date: new Date(),
    amount: 300
  },
  {
    id: "1",
    ref_no: "pa-1234",
    type: "invoice",
    date: new Date(),
    amount: 200
  },
  { id: "1", ref_no: "1", type: "invoice", date: new Date(), amount: 100 },
  { id: "1", ref_no: "1", type: "invoice", date: new Date(), amount: 100 },
  { id: "1", ref_no: "1", type: "invoice", date: new Date(), amount: 100 },
  { id: "1", ref_no: "1", type: "invoice", date: new Date(), amount: 100 },
  { id: "1", ref_no: "1", type: "invoice", date: new Date(), amount: 100 },
  { id: "1", ref_no: "1", type: "invoice", date: new Date(), amount: 100 }
];

/**
 * @title Data table with sorting, pagination, and filtering.
 */
@Component({
  selector: "app-payment-allocation-picker",
  styleUrls: ["./payment-allocation-picker.component.css"],
  templateUrl: "./payment-allocation-picker.component.html"
})
export class PaymentAllocationPickerComponent implements OnInit {
  displayedColumns: string[] = ["ref_no", "type", "date", "amount", "select"];
  dataSource: MatTableDataSource<Allocatable>;
  selection = new SelectionModel<Allocatable>(true, []);

  @ViewChild(MatPaginator)
  paginator: MatPaginator;
  @ViewChild(MatSort)
  sort: MatSort;

  constructor() {
    // Assign the data to the data source for the table to render
    this.dataSource = new MatTableDataSource(allocatables);
  }

  ngOnInit() {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  applyFilter(filterValue: string) {
    this.dataSource.filter = filterValue.trim().toLowerCase();

    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }
}
