import Random, {random} from "../../core/Random";
import HistogramLayout from "./HistogramLayout";
import Bubble from "./Bubble";
import Layout from "./Layout";
import Controller from "./Controller";
import {directRoute, LayoutAnimator} from "./LayoutAnimator";
import MemberBubble from "./MemberBubble";
import Member from "../../core/Member";
import OffscreenLayout from "./OffscreenLayout";
import RangesAndGradients from "./RangesAndGradients";
import CategoryAxis from "./CategoryAxis";
import Point from "./Point";
import * as d3 from "d3"
import CombinedDistrictData from "../../core/CombinedDistrictData";
import ElectionDataManager from "../../core/ElectionDataManager";
import blockTimer from "../../core/BlockTimer";
import SVGSlider from "./SVGSlider";
import DisplayRectangle from "../../VoterRepresentation/DisplayRectangle";
import NumericAxis from "./NumericAxis";


class MemberController extends Controller {
  bubbles: Array<MemberBubble>
  random: Random
  width = 1000
  height = 1000
  radius = 12
  layout: Layout
  animator!: LayoutAnimator | undefined
  ranges = new RangesAndGradients()
  combinedDistrictData: CombinedDistrictData
  electionDataManager?: ElectionDataManager
  svg: d3.Selection<any, any, any, any>
  memberGroupName: string = ""
  slider?: SVGSlider
  congress: number
  simulatedLayout: boolean = false

  // Debug method to track simulatedLayout changes


  constructor(svg: d3.Selection<any, any, any, any>,
              congress: number,
              radius: number,
              combinedDistrictData: CombinedDistrictData,
              electionDataManager?: ElectionDataManager) {
    super()
    this.radius = radius
    this.combinedDistrictData = combinedDistrictData
    this.electionDataManager = electionDataManager

    this.congress = congress
    this.svg = svg;
    ////////////////////////////////////////////////////////////////////////////////

    this.random = new Random()
    // this.layout = new HistogramLayout((b: Bubble) => b.ideology, directRoute,
    //     600, this.ranges.histogramScale, this.radius - 1)
    this.layout = new OffscreenLayout()
    this.bubbles = this.createCongress(congress)

    this.bubbles.forEach(b => {
          b.x = random.intRange(0, 1000)
          b.y = random.intRange(-800, -1000)
          this.setOpacity((b: Bubble) => 0)
        }
    )
    this.sortByIdeology()
  }

  setH2HMembers = () => {
    let h2hMembers = this.combinedDistrictData.districts.map(district => {
      let dw = this.combinedDistrictData.DWNominate.house(117, district)
      let ideology = this.combinedDistrictData.sampleCongress[district].ideology("condorcet")
      return new Member(dw.representativeName, dw.party, ideology / 30, "House", district)
    })
    this.bubbles = h2hMembers.map(m => new MemberBubble(m, this.radius))
  }

  moveOffscreen = (duration: number = 3000) => {
    this.clearAxes()
    this.clearLabel()
    this.setLayout(new OffscreenLayout(-1000, -1000, 0, 1000, duration))
    this.simulatedLayout = false

  }

  sortByParty = () => {
    this.bubbles.sort((a, b) => {
          if (a.irvRound !== b.irvRound)
            return a.irvRound - b.irvRound
          else if (a.party !== b.party)
            return a.party.name < b.party.name ? -1 : 1
          else
            return a.ideology - b.ideology
        }
    )
  }

  createCongress = (congress: number): MemberBubble[] => {
    let cc = this.combinedDistrictData.DWNominate.congresses.get(congress)
    if (cc) {
      let keys: Array<string> = cc ? Array.from(cc.house.keys()) : []
      let members = keys.map(d => {
        let dw = cc!.house.get(d)!
        let ideology = dw.nominateDim1 * this.ranges.dwNominateScale
        return new Member(dw.representativeName, dw.party, ideology, "House", d)
      })
      return members.map(m => new MemberBubble(m, this.radius))
    } else {
      return []
    }
  }

  applyCurrentLayout = () => {
    this.layout.reset()
    this.bubbles.forEach((b) => {
      this.layout.setTargetLocation(b)
    })
  }

  setStandardLabel = () => {
    let congress = this.congress
    let y = this.axes.length > 0 ? this.axes[0].topLeft.y + 75 : 950
    let suffix = [
      "th",
      "st",
      "nd",
      "rd",
      "th",

      "th",
      "th",
      "th",
      "th",
      "th"][congress % 10]

    this.setLabel(`${congress}${suffix} United States Congress (${congress * 2 + 1787})`, 500, y)
  }

  onNewCongress = (congress: number) => {
    congress = Math.round(congress)
    // console.log(`onNewCongress ${congress}`)
    this.bubbles = this.createCongress(congress)
    this.congress = congress
    this.applyCurrentLayout()
    this.applyColorAndOpacity()
    this.renderFrameSVG(0)
    this.setStandardLabel()
  }

  colorByParty = () => {
    this.setColor((b: Bubble) => (b as MemberBubble).member.party.color, "colorByParty")
  }

  clearSlider = () => {
    if (this.slider) {
      this.slider.clear()
      this.slider = undefined
    }
  }

  setLayout = (layout: Layout, name: string = "unspecified") => {
    this.layout = layout
    this.layoutName = name
    this.dirty = true
    // Set simulatedLayout flag based on the layout name
    // Only set to true if explicitly simulation-related, preserve false for actual data
    if (name.includes("condorcet") || name.includes("consensus")) {
      this.simulatedLayout = true
    } else if (name.includes("actual")) {
      this.simulatedLayout = false
    }
    // Don't change simulatedLayout for other cases
  }

  createSlider = (y: number) => {
    if (this.slider) return
    this.slider = new SVGSlider(
        "congressional-slider",
        this.svg,
        new DisplayRectangle(200, y, 600, 40),
        [1, 119],
        119,
        15,
        "black",
        "black",
        "1789",
        "2025",
        (_v: number) => {
        },
        (congress: number) => {
          this.onNewCongress(congress)
        },
        (congress: number) => {
          this.onNewCongress(congress)
        })

    this.slider.render()
  }

  createIdeologyAxis = (svg: d3.Selection<any, any, any, any>, y: number, id: string): CategoryAxis => {
    let categories = ["Very Liberal", "Liberal", "Balanced", "Conservative", "Very Conservative"]
    // let categories = ["Hyper-Partisan", "Partisan", "Non-Partisan", "Partisan ", "Hyper-Partisan "]
    return new CategoryAxis(id, svg, categories, new Point(10, y), 980, "")
  }

  clearLabel = () => {
    this.svg.selectAll(`.${this.memberGroupName}memberLabel`).remove()
  }
  setLabel = (label: string, x: number, y: number) => {
    this.clearLabel()
    this.svg.append("text")
        .attr("class", `${this.memberGroupName}memberLabel`)
        .text(label)
        .attr("x", x)
        .attr("y", y)
        .style("font-size", "18pt")
        .style("text-anchor", "middle")
  }

  colorByIdeology = (): void => {
    this.setColor((b: Bubble) => this.ranges.colorByIdeology(b.ideology), "membersByIdeology")
  }

  colorBySampleIdeology = (simType: string): void => {
    this.setColor((b: Bubble) => {
      let mb = b as MemberBubble
      let ideology = simType === "actual" ?
          mb.member.ideology :
          (this.electionDataManager ? 
            this.electionDataManager.sampleIdeology(simType, mb.member.district) :
            this.combinedDistrictData.sampleIdeology(simType, mb.member.district))
      return this.ranges.colorByIdeology(ideology)
    }, "membersByIdeology")
  }

  layoutByNominate = (svg: d3.Selection<any, any, any, any>, yValue: number, duration: number = 3000): void => {
    this.colorByIdeology()
    this.setOpacity((_b: Bubble) => .9)
    this.setLayout(
        new HistogramLayout((b: Bubble) => (b as MemberBubble).member.nominate,
            directRoute,
            yValue, this.ranges.nominateScale, this.radius - 1, duration),
        "members nominate Layout")
    this.simulatedLayout = false
    this.clearAxes()
    let title = "United States House Members by Nominate Dim-1"
    this.addAxis(new NumericAxis("nominateAxis", svg, this.ranges.nominateScale, [-.75, -.5, -.25, 0, .25, .5, .75], new Point(10, yValue), 980, title, false))
    // this.setStandardLabel()
  }

  layoutByIdeology = (svg: d3.Selection<any, any, any, any>, yValue: number, duration: number = 3000): void => {
    this.colorByIdeology()
    this.setOpacity((_b: Bubble) => .9)
    this.setLayout(
        new HistogramLayout((b: Bubble) => b.ideology,
            directRoute,
            yValue, this.ranges.histogramScale, this.radius - 1, duration),
        "members histogram Layout")
    this.simulatedLayout = false
    this.clearAxes()
    this.addAxis(this.createIdeologyAxis(svg, yValue, `memberAxis`))
    this.setStandardLabel()
  }

  layoutBySampleIdeology = (svg: d3.Selection<any, any, any, any>, simType: string, yValue: number, duration: number = 3000, label: string): void => {
    this.colorBySampleIdeology(simType)
    this.setOpacity((_b: Bubble) => .9)
    this.setLayout(
        new HistogramLayout((b: Bubble) => {
              let mb: MemberBubble = (b as MemberBubble)
              // Use new ElectionDataManager if available, fallback to old CombinedDistrictData
              if (this.electionDataManager) {
                return this.electionDataManager.sampleIdeology(simType, mb.member.district)
              } else {
                return this.combinedDistrictData.sampleIdeology(simType, mb.member.district)
              }
            },
            directRoute,
            yValue, this.ranges.histogramScale, this.radius - 1, duration),
        "members histogram Layout")
    this.simulatedLayout = true
    this.addAxis(this.createIdeologyAxis(svg, yValue, `memberAxis`))
  }

  sortByIdeology = () => {
    this.bubbles.sort((a, b) => {
          return a.ideology - b.ideology
        }
    )
  }

  createMemberVoterAxes = (svg: d3.Selection<any, any, any, any>, policyOrIdeology: string) => {
    let policyCategories = [
      `Liberal ${policyOrIdeology}`,
      `Conservative ${policyOrIdeology}`,
    ]

    let voterCategories = [
      "Republican Leaning",
      "Democratic Leaning",
    ]
    this.addAxis(new CategoryAxis("policyAxis", svg, policyCategories, new Point(50, 500), 900, "", false))
    this.addAxis(new CategoryAxis("voterAxis", svg, voterCategories, new Point(500, 50), 900, "", true))
  }

  render = () => {
    // blockTimer(() => {this._render()}, "MemberController.render()")
    blockTimer(() => {this._renderSVG()}, "MemberController.render()")
  }

  fixNameCase = (name: string): string => {
    return name.toLowerCase().replace(/\b(\w)/g, s => s.toUpperCase());
  }

  mouseOver = (event: MouseEvent, mb: MemberBubble) => {
    // console.log(`mouseover:  mb ${mb.member.district}`)
    let flyover = d3.select(`#detailsFlyover`)

    let memberName = this.simulatedLayout ? "Simulated Winner" : this.fixNameCase(mb.member.name)

    flyover.select("#memberName").html(memberName)
    flyover.select("#districtName").html(mb.member.district)
    flyover.select("#party").html(mb.member.party.name)
    // convert back to raw dwNominate and then multiply by 100.
    let ideology = (this.simulatedLayout) ?
        this.combinedDistrictData.sampleIdeology("condorcet", mb.member.district) :
        mb.member.ideology
    flyover.select("#ideology").html(Math.round(ideology / this.ranges.dwNominateScale * 100) + "")

    if (this.congress === 119) {
      let representation = Math.round(this.combinedDistrictData.actualRepresentation(mb.member.district))
      flyover.select("#representation").html(`Representation Score: ${representation}`)
    } else {
      flyover.select("#representation").html("")
    }

    // @ts-ignore
    let parentRect = flyover!.node()!.parentNode.getBoundingClientRect()
    // @ts-ignore
    let flyoverRect = flyover!.node()!.getBoundingClientRect()
    let x_parent = event.x - parentRect.x
    if (x_parent + flyoverRect.width + 50 > parentRect.width) {
      let right = parentRect.width - x_parent + 20
      flyover.style("right", right + "px")
      flyover.style("left", "")
    } else {
      flyover.style("left", (x_parent + 20) + "px")
      flyover.style("right", "")
    }

    flyover
        .style("top", (event.y - 50) + "px")
        .style("display", "block")

  }
  mouseOut = (event: MouseEvent, mb: MemberBubble) => {
    d3.select(`#detailsFlyover`)
        .style("display", "none")
  }

  renderFrameSVG = (duration: number): void => {
    // console.log(`members.renderFrameSVG: bubbles.size ${this.bubbles.length}`)
    let className = `${this.memberGroupName}members`
    this.svg.selectAll(`.${className}`).data(this.bubbles)
        .join(
// @ts-ignore
            enter => {
              enter
                  .append("circle")
                  .classed(className, true)
                  .attr("cx", (b) => b.tx)
                  .attr("cy", (b) => b.ty)
                  .attr("r", (b) => b.radius)
                  .style("fill", (b) => b.color)
                  .style("opacity", (b) => b.opacity)
                  // .style("stroke", 'black')
                  // .style("stroke-width", 2)
                  .style("cursor", "arrow")
                  .on("mouseover", this.mouseOver)
                  .on("mouseout", this.mouseOut)
            },
            update => {
              if (duration > 10) {
                //@ts-ignore
                update = update.transition("memberUpdate")
                    .duration(1000)
              }

              update.attr("cx", (b) => b.tx)
                  .attr("cy", (b) => b.ty)
                  .style("fill", (b) => b.color)
                  .style("opacity", (b) => b.opacity)
            },
            exit => {
              exit.remove()
            }
        )
  }

  _renderSVG = () => {
    if (!this.dirty) return
    // console.log("members._renderSVG")
    this.applyUpdate()
    this.applyColorAndOpacity()
    this.axes.forEach(axis => axis.render())
    this.layout.reset()
    this.bubbles.forEach((b) => {
      this.layout.setTargetLocation(b)
    })
    // renders only a single frame, but uses d3-transition to move things into place.
    this.renderFrameSVG(this.layout.duration)
    // assume all of the bubbles got where they are going
  }
}

export default MemberController