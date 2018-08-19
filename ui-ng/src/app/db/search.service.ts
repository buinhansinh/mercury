import { Observable } from "rxjs";

export interface SearchService<T> {
  search(terms: String): Observable<T[]>;
}
