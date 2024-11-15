class ClickButton extends React.Component {
  state = {
    wasClicked: false
  }

  handleClick () {
    this.setState(
      {wasClicked: true}
    )
  }

  render () {
    let buttonText

    if (this.state.wasClicked)
      buttonText = 'Clicked!'
    else
      buttonText = 'Click Me'

    return React.createElement(
      'button',
      {
        className: 'btn btn-primary mt-2',
        onClick: () => {
          this.handleClick()
        }
      },
      buttonText
    )
  }
}

/*
ReactDOM.render requires two pieces of information: the component 
to be rendered and the location on the page where it should be 
mounted. React.createElement(myComponent) is the component, so it 
should come first. document.getElementById('myElement') denotes 
the element on the page where the component will be mounted. It 
should come second.
*/
const domContainer = document.getElementById('react_root')
//const domContainer = document.getElementById('root')
ReactDOM.render(
  React.createElement(ClickButton),
  domContainer
)