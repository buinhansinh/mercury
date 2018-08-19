import { Injectable } from "@angular/core";
import { Observable, of } from "rxjs";
import { Offer, OfferType } from "./offer.model";
import { OFFERS } from "./offer.mock";
import { clone } from "../app-common/util";
import { SearchService } from "./search.service";

@Injectable()
export class OfferService implements SearchService<Offer> {
  private OFFERS: Offer[] = OFFERS;

  product: Offer;

  constructor() {}

  getById(id: string): Observable<Offer> {
    return of(OFFERS.find(p => p.id === id));
  }

  private match(offer: Offer, term: string): boolean {
    const lterm = term.toLowerCase();
    return lterm.length < 2
      ? offer.description.toLowerCase().indexOf(lterm) === 0
      : offer.description.toLowerCase().indexOf(lterm) >= 0;
  }

  search(terms: string): Observable<Offer[]> {
    console.log(terms);
    if (terms.trim().length < 1) {
      return of([]);
    }
    const results: Offer[] = this.OFFERS.filter(offer =>
      terms.split(" ").every((term: string): boolean => this.match(offer, term))
    );
    return of(results.length > 0 ? clone(results) : null);
  }
}
