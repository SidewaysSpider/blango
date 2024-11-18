['/api/v1/posts/', '/', '/abadurl/'].forEach(url => {
  fetch(url).then(response => {
    if (response.status !== 200) {
      throw new Error('Invalid status from server: ' + response.statusText)
    }

    return response.json()
  }).then(data => {
    // do something with data, for example
    console.log(data)
  }).catch(e => {
    console.error(e)
  })
})


//The following class is an example of a React Component class
//Start of class ClickButton
class ClickButton extends React.Component {
  state = {
    wasClicked: false
  }

  /*
  handleClick is an event handler
  It is used to update state
  In React, you can only update state with the setState method.
  React lets you reference state, but you cannot assign a new
  value to it as you would a variable.
  */
  handleClick () {
    this.setState(
      {wasClicked: true}
    )
  }

  /*
The component’s render() method should return a React element, which
will be added to a page.
The element can be created with the React.createElement() function. This
takes three arguments:
The first is either the name of the element to create, such as div, span,
etc. Or, it can be another React component as a child.
The second argument object (dictionary) of properties/attributes to set
on the element. These can be standard attributes like id, onClick or
href (depending on what the element supports). Or custom properties
that the child React component supports can be used.
The third is a list of children, this can be a single string, or an 
array of strings or other elements.
 */

  non_jsx_render () {
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

  render () {
    let buttonText

    if (this.state.wasClicked)
      buttonText = 'Clicked!'
    else
      buttonText = 'Click Me'

    return <button
      className="btn btn-primary mt-2"
      onClick={
        () => {
          this.handleClick()
        }
      }
    >
      {buttonText}
    </button>
  }
}
//End of class ClickButton

/*
To mount a component onto the page (or the DOM) we use the
ReactDOM.render() function.

ReactDOM.render requires two arguments: the component (aka react element)
to be rendered and the location on the page where it should be 
mounted (aka DOM element in which to render it).

ClickButton is the component class, and React.createElement(ClickButton))
creates the actual component. It should be the first argument of
ReactDOM.render. document.getElementById('react_root') denotes the 
element on the page where the component will be mounted. It should be
the second argument of ReactDOM.render.
The react_root element is a div element defined in 
blango/templates/blog/post-table.html
*/

const domContainer = document.getElementById('react_root')
ReactDOM.render(
  React.createElement(ClickButton),
  domContainer
)


//-----------------------------------------------
//The following classes support a React based table display
//React Component class
//Start of class PostRow; this is for defining a row component
class PostRow extends React.Component {
  render () {
    const post = this.props.post

    let thumbnail

    if (post.hero_image.thumbnail) {
      thumbnail = <img src={post.hero_image.thumbnail}/>
    } else {
      thumbnail = '-'
    }

    return <tr>
      <td>{post.title}</td>
      <td>
        {thumbnail}
      </td>
      <td>{post.tags.join(', ')}</td>
      <td>{post.slug}</td>
      <td>{post.summary}</td>
      <td><a href={'/post/' + post.slug + '/'}>View</a></td>
    </tr>
  }
}
//End of class PostRow

//Start of class PostTable; this is for defining a table component
class PostTable extends React.Component {
  /*
  state = {
    dataLoaded: true,
    data: {
      results: [
        {
          id: 15,
          tags: [
            'django', 'react'
          ],
          'hero_image': {
            'thumbnail': '/media/__sized__/hero_images/snake-419043_1920-thumbnail-100x100-70.jpg',
            'full_size': '/media/hero_images/snake-419043_1920.jpg'
          },
          title: 'Test Post',
          slug: 'test-post',
          summary: 'A test post, created for Django/React.'
        }
      ]
    }
  }
  */

  state = {
    dataLoaded: false,
    data: null
  }

  /*
   -componentDidMount is called right after a component is added to the
    web page.
   -component WillUnmount called right before a component is removed from
    the web page.
   -componentDidUpdate called when the parent component re-renders and passes
    a different property to the child component.  
    no longer using fetch('/api/v1/posts/').then(response => {
  */
  componentDidMount () {
    fetch(this.props.url).then(response => {
      if (response.status !== 200) {
        throw new Error('Invalid status from server: ' + response.statusText)
      }

      return response.json()
    }).then(data => {
      this.setState({
        dataLoaded: true,
        data: data
      })
    }).catch(e => {
      console.error(e)
      this.setState({
        dataLoaded: true,
        data: {
          results: []
        }
      })
    })
  }

  render () {
    let rows
    if (this.state.dataLoaded) {
      if (this.state.data.results.length) {
        rows = this.state.data.results.map(post => <PostRow post={post} key={post.id}/>)
      } else {
        rows = <tr>
          <td colSpan="6">No results found.</td>
        </tr>
      }
    } else {
      rows = <tr>
        <td colSpan="6">Loading&hellip;</td>
      </tr>
    }

    return <table className="table table-striped table-bordered mt-2">
      <thead>
      <tr>
        <th>Title</th>
        <th>Image</th>
        <th>Tags</th>
        <th>Slug</th>
        <th>Summary</th>
        <th>Link</th>
      </tr>
      </thead>
      <tbody>
      {rows}
      </tbody>
    </table>
  }
}
//End of class PostTable

/*
const domContainer = document.getElementById('react_root')

ReactDOM.render(
  React.createElement(PostTable),
  domContainer
)

ReactDOM.render(
  React.createElement(
    PostTable,
    {url: postListUrl}
  ),
  domContainer
)
*/