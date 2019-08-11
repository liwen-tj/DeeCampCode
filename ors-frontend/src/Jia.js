import React, { Component } from 'react';
import './Jia.css';
import { Tooltip, Drawer, Button } from 'antd';
import { Bar as BarChart, Doughnut } from 'react-chartjs-2';
import API from "./utils/api";
import Legend from "./Legend";
import { PredictChart } from './myChart';
import * as moment from "moment";

const unitPx = 15;

class OperationItem extends Component {
    state = { visible: false };

    showDrawer = () => {
        this.setState({
            visible: true,
        });
    };

    onClose = () => {
        this.setState({
            visible: false,
        });
    };

    render() {
        console.log(this.props.operationDuration, this.props.recoverDuration, this.props.cleanDuration);

        return (<div className="OperationItem"
            style={{ left: this.props.beginIndex * unitPx + "px" }}>
            <div className="TimeTag">
            </div>
            <Tooltip placement="topLeft" title={this.props.secondInfo}>
                <div className="OperationItemBody" onClick={this.showDrawer} style={{ width: this.props.operationDuration * unitPx + "px" }}>
                    {this.props.patientName}
                </div>
            </Tooltip>
            <div className="OperationItemBody"
                style={{ width: this.props.recoverDuration * unitPx + "px", background: '#EB84C0' }}>
            </div>
            <div className="OperationItemBody"
                style={{ width: this.props.cleanDuration * unitPx + "px", background: '#74EDDA' }}>
            </div>

            <div className="TimeTag">
            </div>
            <Drawer
                title="详细信息"
                placement="right"
                closable={false}
                onClose={this.onClose}
                visible={this.state.visible}
                width="30%"
            >
                <PredictChart jieshi_key={this.props.jieshi_key} />
                <div className="display-linebreak">{this.props.thirdInfo}</div>
            </Drawer>
        </div>);
    }
}

function OperationScheduleTable(props) {
    let startTime = props.envSetting.startTime;
    let endTime = props.envSetting.endTime;
    // let startTime = moment(props.envSetting.startTime).format('HH:mm');
    // let endTime = moment(props.envSetting.endTime).format('HH:mm');
    // console.log(startTime);
    // console.log(endTime);

    let workTimeRange = (moment(endTime) - moment(startTime)) / 60000 / unitPx;

    console.log('OperationScheduleTable', workTimeRange);
    let timeQuantum = 24 * 60 / unitPx;
    return (<div>
        <div className={"OperationSchedule"}>
            <table style={{ tableLayout: "fixed", width: "200px" }}>
                {/*-------------------横轴------------------*/}
                <thead className={"stickyRow"}>
                    <tr className={"stickyRow"}>
                        <th className={"stickyRow bedInfo scheduleHeader"} style={{ zIndex: 4 }}>{null}</th>
                        {[...Array(timeQuantum).keys()].map(x => {
                            let timePoint = moment(startTime).add(unitPx * x, 'm').format('HH:mm');
                            return <th key={x}
                                className={"stickyRow scheduleHeader quarterCell" + (workTimeRange === x ? " endTimeCell" : "")}>
                                <div style={{ width: "100%", height: "100%", position: "relative" }}>
                                    <p className={"timeTag"}>
                                        {timePoint.match(/[30]0$/) ? timePoint : null}
                                    </p>
                                    {timePoint.endsWith('00') ? <div className={"timePoint"}>{null}</div> : null}
                                </div>
                            </th>
                        })}
                    </tr>
                </thead>
                {/*-------------------横轴------------------*/}
                <tbody>
                    {props.schedules.map((bedSchedule, bedIdx) => {
                        return ([
                            <tr key={"space" + bedIdx} className={"stickyRow"}>
                                <td className={"bedInfo spaceRow"}>{null}</td>
                                {[...Array(timeQuantum).keys()].map(y => {
                                    return <td className={"quarterCell spaceRow" + (workTimeRange === y ? " endTimeCell" : "")} key={y}>{null}</td>
                                })}
                            </tr>,
                            <tr key={"data" + bedIdx} className={"stickyRow"}>
                                {/*-------纵轴-------*/}
                                <td className={"bedInfo"}>{bedSchedule.roomInfo}</td>
                                {/*-------纵轴-------*/}
                                <td className={"quarterCell dataRow"}>
                                    <div className={"BedScheduleTd"}>
                                        {
                                            bedSchedule.operation.map((x, y) => {
                                                return <OperationItem key={y}
                                                    patientName={x.patientName}
                                                    beginIndex={x.beginIndex}
                                                    operationDuration={x.operationDuration}
                                                    secondInfo={x.secondInfo}
                                                    thirdInfo={x.thirdInfo}
                                                    recoverDuration={x.recoverDuration}
                                                    cleanDuration={x.cleanDuration}
                                                    jieshi_key={x.jieshi_key} />

                                            })
                                        }
                                    </div>
                                </td>
                                {[...Array(timeQuantum - 1).keys()].map(y => {
                                    return <td className={"quarterCell dataRow"} key={y}>{null}</td>
                                })}
                            </tr>
                        ])
                    })}
                    <tr className={"stickyRow"}>
                        <td className={"bedInfo"}>{null}</td>
                        {[...Array(timeQuantum).keys()].map(y => {
                            return <td className={"quarterCell spaceRow" + (workTimeRange === y ? " endTimeCell" : "")} key={y}>{null}</td>
                        })}
                    </tr>
                </tbody>
            </table>
        </div>
    </div>)
}

class Jia extends Component {
    constructor(props) {
        super(props);
    };

    preview = () => { // 预览
        let myscheduleValue = JSON.parse(this.props.scheduleValue);
        let values1 = myscheduleValue.sort(this.compare("orId", "startTime"));
        // console.log(values1);
        fetch(API + '/preview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json; charset=UTF-8',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
            },
            responseType: 'blob',
            body: JSON.stringify(values1)
        }).then(res => {
            if (res.status === 200) {
                return res.blob()
            }
        }).then(function (blob) {
            let blobUrl = window.URL.createObjectURL(blob);
            window.open(blobUrl);
        });
    };

    compare(property1, property2) {
        return function (obj1, obj2) {
            var value1 = obj1[property1];
            var value2 = obj2[property1];
            if (value1 === value2) {
                var a = obj1[property2].split(":");
                var b = obj2[property2].split(":");
                let x = parseInt(a[0]) * 60 + parseInt(a[1]);
                let y = parseInt(b[0]) * 60 + parseInt(b[1]);
                return x - y;
            }
            else {
                return value1 - value2;     // 升序
            }
        }
    }

    genSchedules(data) { // data: values1
        if (data.length == 0) { return [] }

        let orid = data[0]['orId'];
        let index = 0;
        let result = [{ 'roomInfo': 'Room ' + orid, 'operation': [] }];
        let startTime = moment(this.props.envSetting.startTime).format('HH:mm');
        let startTimeArray = startTime.split(":");
        let startTimeMinutes = parseInt(startTimeArray[0]) * 60 + parseInt(startTimeArray[1]);
        console.log(startTimeMinutes);
        for (var dataindex in data) {
            let x = data[dataindex];
            let tmp = {};
            tmp['jieshi_key'] = x['key'];
            tmp['patientName'] = x['name'] + " " + x['startTime'];
            tmp['secondInfo'] = x['name'] + " " + x['startTime'] + " " + x['predTime'] + "分钟 " + x['operatingName'];
            tmp['thirdInfo'] = "就诊号：" + x['id'] + " \n姓名：" + x['name'] + " \n开始时间：" + x['startTime'] + " \n预测手术时长：" + x['predTime'] + "分钟 \n手术名称：" + x['operatingName'];
            let ti = x['startTime'].split(":");
            tmp['beginIndex'] = (parseInt(ti[0]) * 60 + parseInt(ti[1]) - startTimeMinutes) / 5;
            tmp['operationDuration'] = x['predTime'] / 5;
            tmp['recoverDuration'] = x['recoverDuration'] / 5;
            tmp['cleanDuration'] = x['cleanDuration'] / 5;
            if (x['orId'] == orid) {
                result[index]['operation'].push(tmp);
            }
            else {
                orid = x['orId'];
                index += 1;
                result.push({
                    'roomInfo': 'Room ' + x['orId'],
                    'operation': [tmp]
                });
            }
        }
        console.log(result);
        return result;
    }

    render() {
        let myscheduleValue = JSON.parse(this.props.scheduleValue);
        let values1 = myscheduleValue.sort(this.compare("orId", "startTime"));
        let scheds = this.genSchedules(values1);

        console.log(scheds);
        return (
            <div>
                <Legend />
                <OperationScheduleTable schedules={scheds} envSetting={this.props.envSetting} />
                <Button type="primary" onClick={this.preview} style={{ marginLeft: "90%" }} className="previewButton">预览排班表</Button>
            </div>
        )
    };
}

export default Jia;
