export enum OrderTransferStatus {
  NEW = 1,
  COMPLETE = 2,
  CANCELED = 3
}

export interface OrderTransfer {
  id: string;
  date: Date;
  ref_no: string;
  status: OrderTransferStatus;
  quantities: number[];
}

export const EMPTY_ORDER_TRANSFER: OrderTransfer = {
  id: null,
  date: null,
  ref_no: null,
  status: OrderTransferStatus.NEW,
  quantities: null
};
