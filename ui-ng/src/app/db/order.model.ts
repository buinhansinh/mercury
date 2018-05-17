import { OfferType, Offer } from "./offer.model";
import { Contact } from "./contact.model";
import { Document } from "./document.model";

export enum OrderItemType {
    PRODUCT,
    SERVICE,
}

export interface OrderItem {
    offer: Offer;
    custom_description: string;
    quantity: number;
    price: number;
}

export interface OrderPricing {
    suggested: number;
    last: number;
    low: number;
    high: number;
    cost: number;
}

export enum OrderStatus {
    PLACED = 1,
    FULFILLED = 2,
    CANCELED = 3,
}

export interface Order extends Document {
    content: {
        items: OrderItem[];
        total: number;
    }
}
