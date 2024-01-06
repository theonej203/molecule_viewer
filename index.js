const getElementList = (data) =>{
    $(".elementGrid").remove()
    let htmlElement = "<div class='elementGrid'>"
    htmlElement += "<h4>Element number</h4>"
    htmlElement += "<h4>Element code</h4>"
    htmlElement += "<h4>Element name</h4>"
    htmlElement += "<h4>Color 1</h4>"
    htmlElement += "<h4>Color 2</h4>"
    htmlElement += "<h4>Color 3</h4>"
    htmlElement += "<h4>Element radius</h4>"
    htmlElement += "<h4>Delete</h4>"
    const elements = data.split(";")
    elements.forEach(element => {
        elementProperty = element.split(",")
        if(element != ""){
            elementProperty.forEach(property => {
                if(property != ""){
                    htmlElement += "<p>"+property+"</p>"
                }
                else{
                    htmlElement += "<button onclick='deleteElement(this)' id='"+elementProperty[2]+"'> X </button>"
                }
            })
        }
        
    })
    htmlElement = htmlElement + "</div>"
    $("#elementList").append(htmlElement)
    

}


const getMoleculeList = (data) =>{
    $('#moleculeSelector').remove()
    const molecules = data.split(";")
    let htmlElement = "<select name='molecule'id='moleculeSelector' >"
    molecules.forEach(molecule =>{
        if(molecule != ""){
            htmlElement += `<option value='${molecule}'> ${molecule} </option>`
        }
    })
    
    htmlElement += "</select>"
    $("#moleculeSelectorDiv").append(htmlElement)
}


const displaySVG = (data) =>{
    $("#moleculeSvg").remove()
    let moleculeSVG = "<div id='moleculeSvg'>"
    moleculeSVG += data
    moleculeSVG += "</div>"
    $("#molWindow1").append(moleculeSVG)
    //alert("display sucessful")
}

const displayMolecule = () =>{
    
    const moleculeName = $("#moleculeSelector").find('option:selected').text()
    $.post("/displayMolecule",
            {
                molName: moleculeName
            },
            displaySVG
        )
}

const rotateMolecule = () =>{
    const moleculeName = $("#moleculeSelector").find('option:selected').text()
    $.post("/rotateMolecule",
            {
                molName: moleculeName,
                xRot: $("#xRotation").val(),
                yRot: $("#yRotation").val(),
                zRot: $("#zRotation").val()
            },
            displaySVG
        )
}



const resetElementList = (data, status) =>{
    alert(data)
    $.get("/getElements", getElementList)
}





const deleteElement = (element) =>{
    //console.log(element.id)
    $.post("/deleteElement",
            {
                eName: element.id
            },
            resetElementList
        )
}

const newElementFunction = () =>{
    $.post("/newElement",
            { 
                eNum: $("#eNum").val(), 
                eCode: $("#eCode").val(),
                eName: $("#eName").val(),
                eCol1: $("#eCol1").val(),
                eCol2: $("#eCol2").val(),
                eCol3: $("#eCol3").val(),                 
                eRad: $("#eRad").val()
            },
            resetElementList
    )
    for(const element of $('#formParent')){
        element.reset()
    }
}










$(document).ready(function(){
    $('#eButton').click(newElementFunction)
    const page = window.location.pathname.split("/").pop()

    if(page === "index.html"){
        $.get("/getElements", getElementList)
    }else if(page === "molViewer.html"){
        $.get("/getMolecules", getMoleculeList)
        $("#submitMolecule").click(displayMolecule)
        $("#rotateMolecule").click(rotateMolecule)
    }
    
})




