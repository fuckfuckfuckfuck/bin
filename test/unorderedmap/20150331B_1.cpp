#include <iostream>
#include <typeinfo>
#include <hash_map>
#include <set>
#include <boost/unordered_set.hpp>
#include <boost/assign/list_of.hpp>
#include <boost/typeof/typeof.hpp>
#include <boost/random.hpp>
#include <boost\Progress.hpp>
using namespace boost;
using namespace std;
using namespace stdext;
template<typename T>
void fill_set(T &c)
{
  variate_generator<mt19937, uniform_int<>> gen(mt19937(), uniform_int<>(0, 100));
  for (int i = 0; i < 10000; ++i)//插入一万个整数
    c.insert(gen());
}
template<typename T>
void test_perform()
{
  T c;
  cout<<typeid(c).name()<<endl;
  {
    boost::progress_timer t;
    fill_set(c);
  }
  {
    boost::progress_timer t;
    c.count(10);
  }
  {
    boost::progress_timer t;
    c.find(20);
  }
}
int main()
{
  test_perform<multiset<int>>();
  //test_perform<hash_multiset<int>>();
  test_perform<unordered_multiset<int>>();
  system("pause");
  return 0;
}
