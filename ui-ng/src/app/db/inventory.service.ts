import { Injectable } from "@angular/core";
import { Observable, of } from "rxjs";
import { Stock } from "./inventory.model";

@Injectable()
export class InventoryService {
  constructor() {}

  getStock(product_id: string, location_id?: string): Observable<Stock[]> {
    return of([
      {
        location_id: "1",
        location_name: "Default",
        quantity: 10
      },
      {
        location_id: "2",
        location_name: "Location Alpha",
        quantity: 20
      },
      {
        location_id: "3",
        location_name: "Location Bravo",
        quantity: 30
      }
    ]);
  }
}
