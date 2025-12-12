from pydantic import BaseModel,Field
from typing_extensions import List

class PriceInfo(BaseModel):
    """Price information"""
    amount: float = Field(..., description="Price amount")
    currency: str = Field(default="INR", description="Currency code")
    display: str = Field(..., description="Formatted price display")

    @property
    def formatted(self) -> str:
        # Auto-format based on currency
        if self.currency == "INR":
            return f"₹{int(self.amount):,}"
        elif self.currency == "USD":
            return f"${self.amount:,.2f}"
        return f"{self.amount} {self.currency}"
    
class Product(BaseModel):
    """Structured product model with validation"""
    name: str = Field(..., description="Product name")
    concentration: str = Field(..., description="Active ingredient concentration")
    skin_types: List[str] = Field(..., description="Suitable skin types")
    key_ingredients: List[str] = Field(..., description="List of ingredients")
    benefits: List[str] = Field(..., description="Product benefits")
    how_to_use: str = Field(..., description="How to use the product")
    side_effects: str = Field(..., description="Safety warnings and side effects")
    price: PriceInfo = Field(...,  description="Product price including the currency symbol (e.g., ₹699, $29.99, €15).")


class Question(BaseModel):
    """Individual question structure"""
    category: str = Field(
        ...,
        description="Type of question. Example: Informational, Safety, Usage, Purchase, Comparison.",
        examples=["Informational"]
    )
    question: str = Field(..., description="The actual question text")

class QuestionsOutput(BaseModel):
    """Collection of categorized questions"""
    questions: List[Question] = Field(..., description="List of generated questions")
    total_count: int = Field(..., description="Total number of questions")

class BenefitDetail(BaseModel):
    """Individual benefit with description"""
    benefit: str = Field(..., description="Benefit name")
    description: str = Field(..., description="Detailed benefit description")


class BenefitsBlock(BaseModel):
    """Benefits content block"""
    block_type: str = Field(default="benefits", description="Block type identifier")
    content: List[BenefitDetail] = Field(..., description="List of benefits")


class UsageStep(BaseModel):
    """Single usage step"""
    step: str = Field(..., description="Usage step description")


class UsageBlock(BaseModel):
    """Usage instructions content block"""
    block_type: str = Field(default="usage", description="Block type identifier")
    instructions: str = Field(..., description="Main usage instructions")
    steps: List[str] = Field(..., description="Step-by-step instructions")
    frequency: str = Field(..., description="Usage frequency")


class IngredientDetail(BaseModel):
    """Individual ingredient with purpose"""
    name: str = Field(..., description="Ingredient name")
    purpose: str = Field(..., description="Ingredient purpose")


class IngredientsBlock(BaseModel):
    """Ingredients content block"""
    block_type: str = Field(default="ingredients", description="Block type identifier")
    primary: str = Field(..., description="Primary active ingredient")
    supporting: List[str] = Field(..., description="Supporting ingredients")
    details: List[IngredientDetail] = Field(..., description="Detailed ingredient info")


class SafetyBlock(BaseModel):
    """Safety information content block"""
    block_type: str = Field(default="safety", description="Block type identifier")
    warnings: str = Field(..., description="Warning text")
    suitable_for: List[str] = Field(..., description="Suitable skin types")
    precautions: List[str] = Field(..., description="Safety precautions")


class OverviewBlock(BaseModel):
    """Product overview content block"""
    block_type: str = Field(default="overview", description="Block type identifier")
    tagline: str = Field(..., description="Product tagline")
    description: str = Field(..., description="Product description")


class ContentBlocks(BaseModel):
    """All content blocks"""
    benefits_block: BenefitsBlock
    usage_block: UsageBlock
    ingredients_block: IngredientsBlock
    safety_block: SafetyBlock
    overview_block: OverviewBlock


class QuestionAnswer(BaseModel):
    """Single Q&A pair"""
    q: str = Field(..., description="Question text")
    a: str = Field(..., description="Answer text")


class FAQSection(BaseModel):
    """FAQ section with category"""
    category: str = Field(..., description="Section category")
    questions: List[QuestionAnswer] = Field(..., description="Q&A pairs")


class FAQMetadata(BaseModel):
    """FAQ page metadata"""
    generated_at: str = Field(..., description="Generation timestamp")
    question_count: int = Field(..., description="Total questions")


class FAQPage(BaseModel):
    """Complete FAQ page structure"""
    template: str = Field(default="faq_v1", description="Template version")
    product_name: str = Field(..., description="Product name")
    sections: List[FAQSection] = Field(..., description="FAQ sections")
    metadata: FAQMetadata = Field(..., description="Page metadata")

class ProductHero(BaseModel):
    """Product page hero section"""
    product_name: str = Field(..., description="Product name")
    tagline: str = Field(..., description="Product tagline")
    price: PriceInfo = Field(..., description="Price information")


class ProductOverview(BaseModel):
    """Product overview section"""
    description: str = Field(..., description="Product description")
    skin_types: List[str] = Field(..., description="Suitable skin types")
    category: str = Field(..., description="Product category")


class ProductPageMetadata(BaseModel):
    """Product page metadata"""
    generated_at: str = Field(..., description="Generation timestamp")


class ProductPage(BaseModel):
    """Complete product page structure"""
    template: str = Field(default="product_page_v1", description="Template version")
    hero: ProductHero
    overview: ProductOverview
    benefits: List[BenefitDetail]
    ingredients: IngredientsBlock
    usage: UsageBlock
    safety: SafetyBlock
    metadata: ProductPageMetadata


class ComparisonProduct(BaseModel):
    """Product in comparison"""
    name: str
    price: float
    concentration: str
    ingredients: List[str]
    benefits: List[str]
    skin_types: List[str]


class PriceComparison(BaseModel):
    """Price comparison analysis"""
    winner: str = Field(..., description="Product with better price")
    difference: float = Field(..., description="Price difference")
    analysis: str = Field(..., description="Price comparison text")


class IngredientsComparison(BaseModel):
    """Ingredients comparison"""
    common: List[str] = Field(..., description="Common ingredients")
    unique_to_a: List[str] = Field(..., description="Unique to Product A")
    unique_to_b: List[str] = Field(..., description="Unique to Product B")


class BenefitsComparison(BaseModel):
    """Benefits comparison"""
    common: List[str] = Field(..., description="Common benefits")
    unique_to_a: List[str] = Field(..., description="Unique to Product A")
    unique_to_b: List[str] = Field(..., description="Unique to Product B")


class SkinTypeComparison(BaseModel):
    """Skin type suitability"""
    product_a: List[str]
    product_b: List[str]


class ComparisonAnalysis(BaseModel):
    """Comparison analysis"""
    price: PriceComparison
    ingredients: IngredientsComparison
    benefits: BenefitsComparison
    skin_types: SkinTypeComparison


class Recommendation(BaseModel):
    """Recommendation summary"""
    budget_conscious: str = Field(..., description="Budget recommendation")
    analysis: str = Field(..., description="Overall analysis")


class ComparisonMetadata(BaseModel):
    """Comparison page metadata"""
    generated_at: str


class ComparisonPage(BaseModel):
    """Complete comparison page structure"""
    template: str = Field(default="comparison_v1")
    title: str
    products: List[ComparisonProduct]
    comparison: ComparisonAnalysis
    recommendation: Recommendation
    metadata: ComparisonMetadata