import { Table } from 'antd';
import React from 'react';
import data from './data/data';

const renderContent = (value, row, index) => {
    const obj = {
        children: value,
        props: {},
    };
    if (index === 4) {
        obj.props.colSpan = 0;
    }
    return obj;
};

const columns = [
    {
        title: 'Name',
        dataIndex: 'name',
        render: (text, row, index) => {
            if (index < 4) {
                return <a href="javascript:;">{text}</a>;
            }
            return {
                children: <a href="javascript:;">{text}</a>,
                props: {
                    colSpan: 5,
                },
            };
        },
    },
    {
        title: 'Age',
        dataIndex: 'age',
        render: renderContent,
    },
    {
        title: 'Home phone',
        colSpan: 2,
        dataIndex: 'tel',
        render: (value, row, index) => {
            const obj = {
                children: value,
                props: {},
            };
            if (index === 2) {
                obj.props.rowSpan = 2;
            }
            // These two are merged into above cell
            if (index === 3) {
                obj.props.rowSpan = 0;
            }
            if (index === 4) {
                obj.props.colSpan = 0;
            }
            return obj;
        },
    },
    {
        title: 'Phone',
        colSpan: 0,
        dataIndex: 'phone',
        render: renderContent,
    },
    {
        title: 'Address',
        dataIndex: 'address',
        render: renderContent,
    },
];


class Schedule extends React.Component {
    render(){
        return <Table columns={columns} dataSource={data} bordered />
    }
}

export default Schedule;
