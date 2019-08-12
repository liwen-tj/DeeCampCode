import React from 'react';
import { Button, Drawer, Icon, message, Upload } from 'antd';
import './App.css';
import 'antd/dist/antd.css';
import MyForm from './MyForm';
import name from './img/name2.png';
class App extends React.Component {

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

  handleSubmit = e => {
    e.preventDefault();
    this.props.form.validateFields((err, values) => {
      if (!err) {
        console.log('Received values of form: ', values);
      }
    });
  };

  render() {
    const props = {
      name: 'file',
      action: 'http://127.0.0.1:5000/fake_upload',
      headers: {
        authorization: 'authorization-text',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Origin, Content-Type, X-Auth-Token',
      },
      accept: ".csv",
      onChange(info) {
        if (info.file.status !== 'uploading') {
          console.log(info.file, info.fileList);
        }
        if (info.file.status === 'done') {
          message.success(`${info.file.name} 首页文件上传成功, 已建立模型`);
        } else if (info.file.status === 'error') {
          message.error(`${info.file.name} 首页文件上传失败`);
        }
      },
    };
    return (
      <div className="App" >
        <img src={name} alt="name" style={{width:"100%"}}/>
        <div className="head">
          <Upload {...props}>
            <Button className="button1 GradientButton" type="primary" size="large">
              <Icon type="upload" /> 上传历史患者信息表
              </Button>
          </Upload>
          <Button className="button2 GradientButton" type="primary" size="large" onClick={this.showDrawer}>
            构建调度表
              </Button>
          <Drawer
            width="20%"
            title="配置信息"
            placement="right"
            closable={true}
            onClose={this.onClose}
            visible={this.state.visible}
            className="myDrawer"
          >
            <MyForm />
          </Drawer>
        </div>
      </div>
    );
  }
}

export default App;
