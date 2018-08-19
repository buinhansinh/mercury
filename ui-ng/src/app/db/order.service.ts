import { Injectable } from "@angular/core";
import { Observable, of } from "rxjs";
import { OrderPricing, OrderItem } from "./order.model";
import { DocumentType } from "./document.model";
import { clone } from "../app-common/util";

@Injectable()
export class OrderService {
  constructor() {}

  getPricing(
    offerId: string,
    contactId: string,
    doctype: DocumentType
  ): Observable<OrderPricing> {
    return of({
      suggested: 500,
      last: 250,
      low: 200,
      high: 300,
      cost: 175
    });
  }
}
