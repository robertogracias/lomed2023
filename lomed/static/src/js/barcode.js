/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useBus, useService } from "@web/core/utils/hooks";

const { Component, xml } = owl;

export class LomedBarcodeHandlerField extends Component {
    setup() {
        const barcode = useService("barcode");
        useBus(barcode.bus, "barcode_scanned", this.onBarcodeScanned);
    }
    onBarcodeScanned(event) {
        const { barcode } = event.detail;
        this.props.update(barcode);
        try {
            setTimeout(function(){
                try{
                    process_barcode(barcode);
                } catch (error) {
            
                }
            },1000);
        } catch (error) {
            
        }
    }
}

LomedBarcodeHandlerField.template = xml``;
LomedBarcodeHandlerField.props = { ...standardFieldProps };

registry.category("fields").add("lomed_barcode_handler", LomedBarcodeHandlerField);