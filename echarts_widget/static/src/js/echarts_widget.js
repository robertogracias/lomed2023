/** @odoo-module */
import {registry} from "@web/core/registry";
import {loadJS} from "@web/core/assets";

const {Component, onWillStart, useState, useEffect, xml} = owl;

export class FieldChart extends Component {
    async setup() {
        super.setup();
        onWillStart(async () => {
            await loadJS("/echarts_widget/static/src/libs/echarts/echarts.min.js");
        });
        useEffect(() => this._renderChart());
    }

    _renderChart() {
        let self = this;
        //alert(str(this));
        let expresion="[name='"+self.props.name+"']";
        const el = $(expresion)[0]; // $('.echarts_container')[0];
        if (el) {
            // 实例化图表
            try {
                let options = JSON.parse(self.props.value)
                if (options) {
                    let chart = echarts.init(el.children[0]);
                    chart.setOption(options)
                    // 宽度撑满容器
                    setTimeout(() => {
                        chart.resize()
                    }, 200)
                    // 窗口变化时大小自适应
                    $(window).resize(function () {
                        chart.resize()
                    });
                }
            } catch (e) {
                console.log(e)
                self.do_warn(_t(`Data Error: ${e}`));
                return;
            }
        }
    }
}

FieldChart.template = xml`<div class="echarts_container" 
    style="height:100%;width:100%;min-height:200px;min-width:400px;display:block;"/>`
registry.category("fields").add("echarts", FieldChart);
