import { Offer } from "./offer.model";
import { Document } from "./document.model";

export interface Location {
  id: string;
  name: string;
}

export interface Stock {
  location_id: string;
  location_name: string;
  quantity: number;
}

export enum OrderTransferStatus {
  PLACED = 0,
  CANCELED
}

export interface OrderTransfer extends Document {
  content: {
    location: Location;
    items: number[];
  };
}

export interface LocationTransferItem {
  offer: Offer;
}

export interface LocationTransfer {
  origin: Location;
  destination: Location;
  items: LocationTransferItem;
}
